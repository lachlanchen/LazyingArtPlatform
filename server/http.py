"""Unmounted Platform HTTP adapter. The issuer owns all provider/password UI.

No deployment CLI or default issuer: an explicitly qualified owner configuration
must supply the service. This module never calls Coin's private/browser API.
"""
import html
from urllib.parse import parse_qs, urlsplit

import tornado.web

from server.account_client import AccountError


def application(service=None, *, origin='https://platform.lazying.art', cookie_secret=None):
    if origin != 'https://platform.lazying.art':
        raise ValueError('unexpected_platform_origin')
    if service and (not cookie_secret or service.client.config.redirect_uri != origin + '/api/account/callback'):
        raise ValueError('qualified_registration_required')

    class Base(tornado.web.RequestHandler):
        def set_default_headers(self):
            self.set_header('Cache-Control', 'no-store')
            self.set_header('Referrer-Policy', 'no-referrer')
            self.set_header('X-Content-Type-Options', 'nosniff')
            self.set_header('X-Frame-Options', 'DENY')
            self.set_header('Content-Security-Policy', "default-src 'none'; style-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")

        def prepare(self):
            if self.request.host != urlsplit(origin).netloc:
                raise tornado.web.HTTPError(400)
            if self.request.method == 'POST' and self.request.headers.get('Origin') != origin:
                raise tornado.web.HTTPError(403)
            if self.request.path != '/api/account/config' and not service:
                raise tornado.web.HTTPError(503)

        def session(self):
            return self.get_cookie('__Host-lap_session', '')

        def write_error(self, status_code, **kwargs):
            self.finish({'error': {400:'invalid_request',403:'request_not_allowed',404:'not_found',
                401:'sign_in_required',409:'retry',503:'account_temporarily_unavailable'}.get(status_code,'request_failed')})

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
            try:
                if self.session():
                    evidence = await service.identity(self.session())
                    name = html.escape(evidence.identity.display_name or 'LazyingArt member')
                    content = f'<h1>{name}</h1><p>Signed in to your LazyingArt account.</p>'
                    content += '<p>Your LAC summary is not connected here yet. <a href="https://coin.lazying.art/">Open Coin</a>.</p>'
                    content += '<p><a href="https://chat.lazying.art/">Open EchoMind</a></p>'
                    content += '<form method="post" action="/api/account/logout">'+self.xsrf_form_html()+'<button>Sign out of this platform</button></form>'
                else:
                    found = await service.client.discover(require_introspection=True)
                    labels = {'password':'Email','google':'Google','apple':'Apple','github':'GitHub'}
                    names = ', '.join(labels[p] for p in found.providers)
                    content = '<h1>Your LazyingArt account</h1><p>Sign in or create an account at the shared account service.</p>'
                    content += '<p>'+html.escape(names)+'</p>'
                    if found.providers:
                        content += '<form method="post" action="/api/account/start">'+self.xsrf_form_html()+'<button>Continue to sign in or sign up</button></form>'
            except AccountError as exc:
                self.fail(exc)
            self.set_header('Content-Type','text/html; charset=utf-8')
            self.write('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>LazyingArt account</title><link rel="stylesheet" href="/styles.css"><body><main class="wrap legal">'+content+'<p><a href="/">Back to products</a></p></main></body></html>')

    class Start(Base):
        async def post(self):
            try:
                browser, url = await service.start()
            except AccountError as exc:
                self.fail(exc)
            self.set_cookie('__Host-lap_flow', browser, secure=True, httponly=True, samesite='Lax',path='/',max_age=600)
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
            except AccountError as exc:
                self.fail(exc)
            self.write({'display_name':evidence.identity.display_name,
                'account_status':'active','coin':{'state':'not_connected','balance':None,'grants':None}})

    class Logout(Base):
        async def post(self):
            confirmed = True
            if self.session():
                try:
                    confirmed = await service.logout(self.session())
                except AccountError:
                    confirmed = False
            self.clear_cookie('__Host-lap_session',path='/',secure=True,httponly=True,samesite='Strict')
            self.write({'signed_out':True,'central_revocation_confirmed':confirmed})

    return tornado.web.Application([
        ('/api/account/config',Configuration),('/account',AccountPage),
        ('/api/account/start',Start),('/api/account/callback',Callback),
        ('/api/account/me',Me),('/api/account/logout',Logout)],
        xsrf_cookies=True,xsrf_cookie_name='__Host-lap_csrf',
        xsrf_cookie_kwargs=dict(secure=True,httponly=True,samesite='Strict',path='/'),
        cookie_secret=cookie_secret,debug=False,
        log_function=lambda handler: None)
