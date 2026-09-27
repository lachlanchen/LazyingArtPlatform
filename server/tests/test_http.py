import json
import re
from types import SimpleNamespace
from unittest.mock import AsyncMock
from urllib.parse import urlencode

from tornado.testing import AsyncHTTPTestCase

from server.account_client import AccountError, Discovery, Identity, IdentityEvidence
from server.http import application

ORIGIN = 'https://platform.lazying.art'
ISSUER = 'https://accounts.example.test'


class DisabledTests(AsyncHTTPTestCase):
    def get_app(self):
        return application()

    def test_disabled_does_not_imply_zero_or_providers(self):
        response = self.fetch('/api/account/config',headers={'Host':'platform.lazying.art'})
        assert json.loads(response.body) == dict(enabled=False,providers=[],coin_connected=False)
        assert response.headers['Cache-Control'] == 'no-store'
        assert self.fetch('/api/account/me',headers={'Host':'platform.lazying.art'}).code == 503

    def test_foreign_host_rejected(self):
        assert self.fetch('/api/account/config',headers={'Host':'evil.example'}).code == 400

    def test_disabled_page_has_no_login_or_balance_fabrication(self):
        response=self.fetch('/account',headers={'Host':'platform.lazying.art'})
        assert response.code==200 and b'not available here yet' in response.body
        assert b'<form' not in response.body and b'0 LAC' not in response.body
        assert response.headers['X-Robots-Tag']=='noindex, nofollow'


class AdapterTests(AsyncHTTPTestCase):
    def get_app(self):
        self.service = SimpleNamespace()
        self.service.client = SimpleNamespace(config=SimpleNamespace(
            issuer=ISSUER,redirect_uri=ORIGIN+'/api/account/callback'))
        self.service.client.discover = AsyncMock(return_value=Discovery(ISSUER,('google','apple','github')))
        self.service.start = AsyncMock(return_value=('b'*48,ISSUER+'/account/authorize?state=fixture'))
        self.service.complete = AsyncMock(return_value='s'*48)
        self.service.logout = AsyncMock(return_value=True)
        self.service.identity = AsyncMock(return_value=IdentityEvidence(
            Identity(ISSUER,'la_'+'a'*32,'<script>private</script>','platform-web'),True,1000))
        return application(self.service,cookie_secret='synthetic-test-cookie-secret-only')

    def request(self, path, **kwargs):
        headers = {'Host':'platform.lazying.art',**kwargs.pop('headers',{})}
        return self.fetch(path,headers=headers,follow_redirects=False,**kwargs)

    def csrf(self):
        response = self.request('/account')
        cookie = next(c for c in response.headers.get_list('Set-Cookie') if c.startswith('__Host-lap_csrf='))
        token = re.search(r'name="_xsrf" value="([^"]+)"',response.body.decode())[1]
        return cookie.split(';',1)[0],token

    def test_chooser_does_not_implement_provider_password_forms(self):
        response = self.request('/account')
        text = response.body.decode()
        assert 'Google · Apple · GitHub' in text
        assert 'type="password"' not in text and 'provider/' not in text
        assert '/api/account/start' in text
        assert self.request('/api/account/start').code == 405

    def test_start_is_same_origin_and_csrf_protected(self):
        assert self.request('/api/account/start',method='POST',body='',headers={'Origin':ORIGIN}).code == 403
        cookie,token = self.csrf()
        body=urlencode({'_xsrf':token})
        assert self.request('/api/account/start',method='POST',body=body,headers={'Origin':'https://coin.lazying.art','Cookie':cookie}).code == 403
        self.service.start.assert_not_awaited()
        response=self.request('/api/account/start',method='POST',body=body,headers={'Origin':ORIGIN,'Cookie':cookie})
        assert response.code == 303
        assert response.headers['Location'].startswith(ISSUER+'/account/authorize?')
        flow=response.headers['Set-Cookie']
        assert '__Host-lap_flow=' in flow and 'Secure' in flow and 'HttpOnly' in flow and 'SameSite=Lax' in flow
        assert 'Domain=' not in flow

    def test_wrong_issuer_preserves_old_login_without_exchange(self):
        query=urlencode(dict(iss='https://evil.example',state='a'*48,code='c'*48))
        response=self.request('/api/account/callback?'+query,headers={'Cookie':'__Host-lap_session=existing'})
        assert response.code == 303 and response.headers['Location']=='/account?result=retry'
        assert not response.headers.get_list('Set-Cookie')
        self.service.complete.assert_not_awaited()
        self.service.logout.assert_not_awaited()

    def test_success_sets_only_host_scoped_app_cookie(self):
        query=urlencode(dict(iss=ISSUER,state='a'*48,code='c'*48))
        response=self.request('/api/account/callback?'+query,headers={'Cookie':'__Host-lap_flow='+'b'*48})
        assert response.code==303 and response.headers['Location']=='/account'
        cookies=response.headers.get_list('Set-Cookie')
        cookie=next(c for c in cookies if c.startswith('__Host-lap_session='))
        assert 'Secure' in cookie and 'HttpOnly' in cookie and 'SameSite=Strict' in cookie and 'Path=/' in cookie
        assert all('Domain=' not in c and 'lac_session=' not in c for c in cookies)
        assert b'c'*48 not in response.body

    def test_display_name_escaped_and_missing_coin_not_zero(self):
        response=self.request('/account',headers={'Cookie':'__Host-lap_session='+'s'*48})
        assert b'<script>private</script>' not in response.body
        assert b'&lt;script&gt;private&lt;/script&gt;' in response.body
        response=self.request('/api/account/me',headers={'Cookie':'__Host-lap_session='+'s'*48})
        data=json.loads(response.body)
        assert data['coin']==dict(state='not_connected',balance=None,grants=None)
        assert set(data)=={'display_name','account_status','coin'}

    def test_outage_does_not_clear_session_or_show_password_failure(self):
        self.service.identity.side_effect=AccountError('account_service_unavailable')
        response=self.request('/api/account/me',headers={'Cookie':'__Host-lap_session='+'s'*48})
        assert response.code==503 and not response.headers.get_list('Set-Cookie')
        assert json.loads(response.body)=={'error':'account_temporarily_unavailable'}

    def test_logout_clears_local_cookie_even_if_revoke_is_unconfirmed(self):
        cookie,token=self.csrf()
        self.service.logout.return_value=False
        response=self.request('/api/account/logout',method='POST',body=urlencode({'_xsrf':token}),
            headers={'Origin':ORIGIN,'Cookie':cookie+'; __Host-lap_session='+'s'*48})
        assert response.code==200
        assert json.loads(response.body)==dict(signed_out=True,central_revocation_confirmed=False)
        assert '__Host-lap_session=' in response.headers['Set-Cookie']

    def test_expired_cookie_gets_a_sign_in_path(self):
        self.service.identity.side_effect=AccountError('account_reconnect_required')
        response=self.request('/account',headers={'Cookie':'__Host-lap_session='+'s'*48})
        assert response.code==303 and response.headers['Location']=='/account?result=retry'
        assert '__Host-lap_session=' in response.headers['Set-Cookie']

    def test_browser_logout_returns_to_account(self):
        cookie,token=self.csrf()
        self.service.logout.return_value=False
        response=self.request('/api/account/logout',method='POST',
            body=urlencode({'_xsrf':token,'return_to':'account'}),
            headers={'Origin':ORIGIN,'Cookie':cookie+'; __Host-lap_session='+'s'*48})
        assert response.code==303 and response.headers['Location']=='/account?result=signed-out-local'


class CoinDashboardTests(AdapterTests):
    def get_app(self):
        super().get_app()
        from test_coin_client import sample
        self.summary=sample()
        self.summary['account']['issuer']=ISSUER
        self.service.coin_summary=AsyncMock(return_value={'state':'available','summary':self.summary})
        self.reader=object()
        return application(self.service,cookie_secret='synthetic-test-cookie-secret-only',coin_reader=self.reader)

    def test_display_name_escaped_and_missing_coin_not_zero(self):
        response=self.request('/account',headers={'Cookie':'__Host-lap_session='+'s'*48})
        assert b'<script>private</script>' not in response.body
        assert b'500 LAC' in response.body and b'1,500 LAC' not in response.body
        assert b'Historical receipts are not an additional spendable balance.' in response.body
        response=self.request('/api/account/me',headers={'Cookie':'__Host-lap_session='+'s'*48})
        assert json.loads(response.body)['coin']['state']=='available'

    def test_read_endpoint_uses_session_not_subject_parameter(self):
        response=self.request('/api/account/coin?subject=other',headers={'Cookie':'__Host-lap_session='+'s'*48})
        assert response.code==400
        self.service.coin_summary.assert_not_awaited()
        response=self.request('/api/account/coin',headers={'Cookie':'__Host-lap_session='+'s'*48})
        assert response.code==200 and response.headers['Cache-Control']=='no-store'
        assert self.service.coin_summary.await_args.args[0]=='s'*48

    def test_connect_is_authenticated_explicit_and_csrf_protected(self):
        cookie,token=self.csrf()
        assert self.request('/api/account/coin/connect').code==405
        assert self.request('/api/account/coin/connect',method='POST',body='',headers={'Origin':ORIGIN}).code==403
        response=self.request('/api/account/coin/connect',method='POST',body=urlencode({'_xsrf':token}),
            headers={'Origin':ORIGIN,'Cookie':cookie+'; __Host-lap_session='+'s'*48})
        assert response.code==303
        self.service.start.assert_awaited_once_with(coin=True)

    def test_no_permission_shows_read_only_choice_not_quantity(self):
        self.service.coin_summary.return_value={'state':'permission_required','summary':None}
        response=self.request('/account',headers={'Cookie':'__Host-lap_session='+'s'*48})
        assert b'Choose Coin read access' in response.body and b'500 LAC' not in response.body
        assert b'move coins or grant spending rights' in response.body

    def test_account_revoked_after_coin_io_does_not_return_snapshot(self):
        self.service.coin_summary.side_effect=AccountError('account_authorization_required')
        response=self.request('/api/account/coin',headers={'Cookie':'__Host-lap_session='+'s'*48})
        assert response.code==401 and b'500' not in response.body
