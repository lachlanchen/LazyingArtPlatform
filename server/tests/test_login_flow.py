"""HTTP + real Platform session store; synthetic central issuer/resource only."""
import json
import re
import tempfile
from types import SimpleNamespace
from urllib.parse import parse_qs, urlencode, urlsplit

from cryptography.fernet import Fernet
from tornado.testing import AsyncHTTPTestCase

from server.account_client import AccountClient, ClientConfiguration, COIN_SCOPE, EXCHANGE_GRANT, pkce_challenge
from server.account_sessions import AccountSessions, SessionStore
from server.coin_client import CoinSummaryClient
from server.http import application
from server.storage import Database
from test_coin_delegation import document, exchange, IDENTITY
from test_coin_client import sample

ORIGIN='https://platform.lazying.art'


class Issuer:
    def __init__(self):
        self.tokens={};self.scope='profile';self.challenge=None
        self.codes=0;self.replay=False

    async def fetch(self,url,**kwargs):
        if url.endswith('/.well-known/lazyingart-account'):
            result=document()
        else:
            if kwargs['headers']['Content-Type']=='application/json':
                body=json.loads(kwargs['body'])
            else:
                body={k:v[0] for k,v in parse_qs(kwargs['body']).items()}
            assert body['client_id']=='lazyingart-platform-web'
            assert body['client_secret']=='synthetic-secret-'+'s'*32
            if url.endswith('/account/token') and body.get('grant_type')=='authorization_code':
                assert body['audience']=='lazyingart-platform-api'
                assert pkce_challenge(body['code_verifier'])==self.challenge
                assert body['redirect_uri']==ORIGIN+'/api/account/callback'
                self.codes+=1
                access='a'+str(self.codes).zfill(47);refresh='r'+str(self.codes).zfill(47)
                entry={'access':access,'refresh':refresh,'scope':self.scope,'active':True}
                self.tokens[access]=self.tokens[refresh]=entry
                result=dict(access_token=access,refresh_token=refresh,token_type='Bearer',scope=self.scope,expires_in=600)
            elif url.endswith('/account/introspect'):
                entry=self.tokens.get(body['token'])
                if not entry or not entry['active']:
                    result={'active':False}
                else:
                    result={'active':True,'iss':IDENTITY.issuer,'client_id':IDENTITY.client_id,
                        'aud':'lazyingart-platform-api','scope':entry['scope'],'token_type':'Bearer',
                        'iat':1000,'exp':1600,'auth_time':1000,'sub':IDENTITY.subject,
                        'account':{'subject':IDENTITY.subject,'display_name':'Synthetic QA member',
                            'account_status':'active','email_verified':True},'verified_legacy_identities':[]}
            elif body.get('grant_type')==EXCHANGE_GRANT:
                assert body['audience']=='lazyartcoin-read-api'
                assert body['scope']=='coin.summary.read'
                assert self.tokens[body['subject_token']]['scope']==COIN_SCOPE
                assert self.tokens[body['subject_token']]['active']
                result=exchange()
            elif url.endswith('/account/revoke'):
                self.tokens[body['token']]['active']=False
                result={'success':True}
            else:
                raise AssertionError('Unexpected synthetic issuer route')
        return SimpleNamespace(code=200,body=json.dumps(result).encode(),headers={'Content-Type':'application/json'})


class Resource:
    async def fetch(self,url,**kwargs):
        assert url=='https://coin.lazying.art/api/integrations/v1/me'
        assert kwargs['headers']=={'Accept':'application/json','X-Lac-Read-Token':'d'*48}
        assert kwargs['method']=='GET' and kwargs['follow_redirects'] is False
        return SimpleNamespace(code=200,body=json.dumps(sample()).encode(),headers={'Content-Type':'application/json'})


class FlowTests(AsyncHTTPTestCase):
    def get_app(self):
        self.temp=tempfile.TemporaryDirectory(prefix='platform-account-test-')
        self.issuer=Issuer()
        client=AccountClient(ClientConfiguration(IDENTITY.issuer,IDENTITY.client_id,'lazyingart-platform-api',
            ORIGIN+'/api/account/callback','synthetic-secret-'+'s'*32),http=self.issuer,clock=lambda:1000)
        store=SessionStore(Database(self.temp.name+'/accounts.sqlite3'),Fernet.generate_key(),client)
        store.install_schema()
        service=AccountSessions(client,store)
        reader=CoinSummaryClient(http=Resource(),clock=lambda:1000)
        self.cookies={}
        return application(service,cookie_secret='synthetic-cookie-secret-'+'s'*32,coin_reader=reader)

    def tearDown(self):
        super().tearDown()
        self.temp.cleanup()

    def request(self,path,*,method='GET',body=None):
        headers={'Host':'platform.lazying.art','Cookie':'; '.join(k+'='+v for k,v in self.cookies.items())}
        if method=='POST':
            headers['Origin']=ORIGIN
        response=self.fetch(path,method=method,body=body,headers=headers,follow_redirects=False)
        for value in response.headers.get_list('Set-Cookie'):
            key,data=value.split(';',1)[0].split('=',1)
            if data=='""':
                self.cookies.pop(key,None)
            else:
                self.cookies[key]=data
        return response

    def csrf(self):
        response=self.request('/account')
        return re.search(r'name="_xsrf" value="([^"]+)"',response.body.decode())[1]

    def login(self,*,coin=False):
        token=self.csrf()
        response=self.request('/api/account/coin/connect' if coin else '/api/account/start',
            method='POST',body=urlencode({'_xsrf':token}))
        assert response.code==303
        auth=parse_qs(urlsplit(response.headers['Location']).query)
        self.issuer.scope=auth['scope'][0]
        self.issuer.challenge=auth['code_challenge'][0]
        callback='/api/account/callback?'+urlencode({'code':'c'*48,'state':auth['state'][0],'iss':IDENTITY.issuer})
        response=self.request(callback)
        assert response.code==303 and response.headers['Location']=='/account'
        assert '__Host-lap_session' in self.cookies
        return callback

    def test_login_consent_coin_and_logout_through_real_platform_handlers(self):
        self.login()
        page=self.request('/account')
        assert b'Synthetic QA member' in page.body and b'Choose Coin read access' in page.body
        assert b'500 LAC' not in page.body
        old=self.cookies['__Host-lap_session']
        callback=self.login(coin=True)
        assert self.cookies['__Host-lap_session']!=old
        data=json.loads(self.request('/api/account/coin').body)
        assert data['state']=='available' and data['summary']['on_chain']['lac_units']=='500000000000000000000'
        page=self.request('/account')
        assert b'500 LAC' in page.body
        assert b'1000 LAC' in page.body
        assert b'1500 LAC' not in page.body
        assert b'dddddddddddddddd' not in page.body
        codes=self.issuer.codes
        replay=self.request(callback)
        assert replay.headers['Location']=='/account?result=retry' and self.issuer.codes==codes
        token=self.csrf()
        response=self.request('/api/account/logout',method='POST',body=urlencode({'_xsrf':token,'return_to':'account'}))
        assert response.headers['Location']=='/account?result=signed-out'
        assert '__Host-lap_session' not in self.cookies
        assert self.request('/api/account/me').code==401

    def test_cancellation_keeps_prior_profile_session(self):
        self.login()
        old=self.cookies['__Host-lap_session']
        token=self.csrf()
        response=self.request('/api/account/coin/connect',method='POST',body=urlencode({'_xsrf':token}))
        auth=parse_qs(urlsplit(response.headers['Location']).query)
        response=self.request('/api/account/callback?'+urlencode({'error':'access_denied','iss':IDENTITY.issuer,'state':auth['state'][0]}))
        assert response.headers['Location']=='/account?result=retry'
        assert self.cookies['__Host-lap_session']==old
        assert self.request('/api/account/me').code==200
