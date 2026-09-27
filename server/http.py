"""Platform account UI/API; central owns all provider/password UI.

The explicit private runtime must supply a qualified registration. The optional
Coin client uses only its separate scoped resource, never the legacy browser API.
"""
import time
from urllib.parse import parse_qs, urlsplit

import tornado.web

from server.account_client import AccountError
from server import views


class RequestBudget:
    """Bound work per process, without trusting forwarded IPs or storing visitors."""
    def __init__(self, *, capacity=60, per_second=2, concurrent=16, clock=time.monotonic):
        self.capacity, self.per_second, self.concurrent = capacity, per_second, concurrent
        self.clock, self.tokens, self.active, self.updated = clock, capacity, 0, clock()

    def acquire(self):
        now = self.clock()
        self.tokens = min(self.capacity, self.tokens + max(0, now-self.updated)*self.per_second)
        self.updated = now
        if self.active >= self.concurrent or self.tokens < 1:
            return False
        self.tokens -= 1
        self.active += 1
        return True

    def release(self):
        self.active -= 1


def application(service=None, *, origin='https://platform.lazying.art', cookie_secret=None, coin_reader=None, request_budget=None):
    if origin != 'https://platform.lazying.art':
        raise ValueError('unexpected_platform_origin')
    if service and (not cookie_secret or service.client.config.redirect_uri != origin + '/api/account/callback'):
        raise ValueError('qualified_registration_required')
    budget = request_budget if request_budget is not None else RequestBudget()

    class Base(tornado.web.RequestHandler):
        def set_default_headers(self):
            self.set_header('Cache-Control', 'no-store')
            self.set_header('X-Robots-Tag', 'noindex, nofollow')
            self.set_header('Referrer-Policy', 'no-referrer')
            self.set_header('X-Content-Type-Options', 'nosniff')
            self.set_header('X-Frame-Options', 'DENY')
            self.set_header('Content-Security-Policy', "default-src 'none'; img-src 'self'; style-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")

        def prepare(self):
            if self.request.host != urlsplit(origin).netloc:
                raise tornado.web.HTTPError(400)
            if self.request.method == 'POST' and self.request.headers.get('Origin') != origin:
                raise tornado.web.HTTPError(403)
            if self.request.path not in ('/api/account/config','/account','/healthz') and not service:
                raise tornado.web.HTTPError(503)
            if self.request.path != '/healthz':
                if not budget.acquire():
                    self.set_header('Retry-After', '1')
                    raise tornado.web.HTTPError(429)
                self._budget_acquired = True

        def on_finish(self):
            if getattr(self, '_budget_acquired', False):
                self._budget_acquired = False
                budget.release()

        async def summary(self, identity):
            if coin_reader is None:
                return {'state':'not_connected','summary':None}
            return await service.coin_summary(self.session(), coin_reader, identity)

        def session(self):
            return self.get_cookie('__Host-lap_session', '')

        def write_error(self, status_code, **kwargs):
            if status_code in (409,429):
                self.set_header('Retry-After', '1')
            self.finish({'error': {400:'invalid_request',403:'request_not_allowed',404:'not_found',
                401:'sign_in_required',409:'retry',429:'try_again_shortly',503:'account_temporarily_unavailable'}.get(status_code,'request_failed')})

        def fail(self, exc):
            if str(exc) == 'account_refresh_in_progress':
                self.set_header('Retry-After', '1')
                raise tornado.web.HTTPError(409)
            if str(exc) in ('account_authorization_required', 'account_reconnect_required', 'invalid_account_identity'):
                raise tornado.web.HTTPError(401)
            raise tornado.web.HTTPError(503)

    class Configuration(Base):
        async def get(self):
            if not service:
                self.write({'enabled':False,'providers':[],'coin_connected':False})
                return
            try:
                found = await service.client.discover(require_introspection=True)
            except AccountError:
                self.set_status(503)
                self.write({'enabled':False,'providers':[],'coin_connected':False})
                return
            self.write({'enabled':True,'providers':list(found.providers),'account_path':'/account', 'coin_connected':False})

    class AccountPage(Base):
        async def get(self):
            message = {'retry':'Sign-in was not completed. Your previous session was kept.',
                'signed-out':'You are signed out of this platform.',
                'signed-out-local':'You are signed out here. The account service could not confirm remote revocation.'}.get(self.get_query_argument('result',''),'')
            if not service:
                self.set_header('Content-Type','text/html; charset=utf-8')
                self.write(views.page(views.sign_in((),'',message=message)))
                return
            try:
                if self.session():
                    evidence = await service.identity(self.session())
                    coin = await self.summary(evidence.identity)
                    content = views.dashboard(evidence.identity, coin, self.xsrf_form_html(),
                        can_connect=coin_reader is not None,
                        account_url=service.client.config.issuer+'/account', message=message)
                else:
                    found = await service.client.discover(require_introspection=True)
                    content = views.sign_in(found.providers,self.xsrf_form_html(),message=message)
            except AccountError as exc:
                if str(exc) in ('account_authorization_required','account_reconnect_required','invalid_account_identity'):
                    self.clear_cookie('__Host-lap_session',path='/',secure=True,httponly=True,samesite='Strict')
                    self.redirect('/account?result=retry',status=303)
                    return
                self.fail(exc)
            self.set_header('Content-Type','text/html; charset=utf-8')
            self.write(views.page(content))

    class Start(Base):
        async def post(self):
            try:
                browser, url = await service.start()
            except AccountError as exc:
                self.fail(exc)
            self.set_cookie('__Host-lap_flow', browser, secure=True, httponly=True, samesite='Lax',path='/',max_age=600)
            self.redirect(url,status=303)

    class ConnectCoin(Base):
        async def post(self):
            if coin_reader is None:
                raise tornado.web.HTTPError(503)
            try:
                await service.identity(self.session())
                browser,url = await service.start(coin=True)
            except AccountError as exc:
                self.fail(exc)
            self.set_cookie('__Host-lap_flow',browser,secure=True,httponly=True,samesite='Lax',path='/',max_age=600)
            self.redirect(url,status=303)

    class Callback(Base):
        async def get(self):
            try:
                fields = parse_qs(self.request.query,keep_blank_values=True,strict_parsing=True,max_num_fields=8)
                if fields.get('iss') != [service.client.config.issuer] or len(fields.get('state',[])) != 1:
                    raise AccountError('callback_binding_mismatch')
                opaque = await service.complete(fields['state'][0],self.get_cookie('__Host-lap_flow',''),
                    service.client.config.redirect_uri+'?'+self.request.query)
            except (AccountError, ValueError):
                # Keep any previous session and return no code/token in the URL.
                self.redirect('/account?result=retry',status=303)
                return
            previous = self.session()
            if previous:
                try:
                    await service.logout(previous)
                except AccountError:
                    pass
            self.clear_cookie('__Host-lap_flow',path='/',secure=True,httponly=True,samesite='Lax')
            self.set_cookie('__Host-lap_session',opaque,path='/',secure=True,httponly=True,samesite='Strict',max_age=30*86400)
            self.redirect('/account',status=303)

    class Me(Base):
        async def get(self):
            try:
                evidence = await service.identity(self.session())
                coin = await self.summary(evidence.identity) if coin_reader is not None else {'state':'not_connected','balance':None,'grants':None}
            except AccountError as exc:
                self.fail(exc)
            self.write({'display_name':evidence.identity.display_name,
                'account_status':'active','coin':coin})

    class Coin(Base):
        async def get(self):
            if self.request.query:
                raise tornado.web.HTTPError(400)
            try:
                evidence = await service.identity(self.session())
                self.write(await self.summary(evidence.identity))
            except AccountError as exc:
                self.fail(exc)

    class Logout(Base):
        async def post(self):
            confirmed = True
            if self.session():
                try:
                    confirmed = await service.logout(self.session())
                except AccountError:
                    confirmed = False
            self.clear_cookie('__Host-lap_session',path='/',secure=True,httponly=True,samesite='Strict')
            self.clear_cookie('__Host-lap_flow',path='/',secure=True,httponly=True,samesite='Lax')
            if self.get_body_argument('return_to','') == 'account':
                self.redirect('/account?result='+('signed-out' if confirmed else 'signed-out-local'),status=303)
                return
            self.write({'signed_out':True,'central_revocation_confirmed':confirmed})

    class Health(Base):
        async def get(self):
            self.write({'service':'lazyingart-platform-account','status':'ok','account_enabled':service is not None})

    return tornado.web.Application([
        ('/api/account/config',Configuration),('/account',AccountPage),
        ('/api/account/start',Start),('/api/account/callback',Callback),
        ('/api/account/me',Me),('/api/account/logout',Logout),
        ('/api/account/coin',Coin),('/api/account/coin/connect',ConnectCoin),('/healthz',Health)],
        xsrf_cookies=True,xsrf_cookie_name='__Host-lap_csrf',
        xsrf_cookie_kwargs=dict(secure=True,httponly=True,samesite='Strict',path='/'),
        cookie_secret=cookie_secret,debug=False,
        log_function=lambda handler: None)
