"""Accepted contract tests only; no live issuer or resource is contacted."""
import asyncio
from dataclasses import replace
import json
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

import pytest
from tornado.httpclient import HTTPRequest

from server.account_client import (ACCESS_TOKEN_TYPE, COIN_DELEGATION, COIN_SCOPE,
    EXCHANGE_GRANT, AccountClient, AccountError, ClientConfiguration, Credentials,
    Discovery, Identity)
from server.coin_client import CoinError
from test_account_client import discovery, token_response

ISSUER='https://accounts.example.test'
IDENTITY=Identity(ISSUER,'la_'+'a'*32,'Example','lazyingart-platform-web')
TOKENS=Credentials('a'*48,'r'*48,1600,COIN_SCOPE)


def document(**changes):
    return discovery(introspection_endpoint=ISSUER+'/account/introspect',
        grant_types_supported=['authorization_code','refresh_token',EXCHANGE_GRANT],
        scopes_supported=['profile','coin.summary.read'],
        adapter_contracts=['platform-coin-read-v1'],resource_delegations=[dict(COIN_DELEGATION)]) | changes


def exchange(**changes):
    return dict(access_token='d'*48,issued_token_type=ACCESS_TOKEN_TYPE,
        token_type='Bearer',expires_in=300,scope='coin.summary.read') | changes


class Transport:
    def __init__(self,*replies):
        self.replies=list(replies);self.requests=[]

    async def fetch(self,url,**kwargs):
        assert kwargs.pop('raise_error') is False
        req=HTTPRequest(url,**kwargs)
        assert not req.follow_redirects and req.validate_cert
        self.requests.append(req)
        reply=self.replies.pop(0)
        if isinstance(reply,BaseException):
            raise reply
        if isinstance(reply,dict):
            return SimpleNamespace(code=200,body=json.dumps(reply).encode(),headers={'Content-Type':'application/json'})
        return reply


def api(*replies):
    transport=Transport(*replies)
    config=ClientConfiguration(ISSUER,'lazyingart-platform-web','lazyingart-platform-api',
        'https://platform.lazying.art/api/account/callback','synthetic-secret-'+'s'*32)
    return AccountClient(config,http=transport,clock=lambda:1000),transport


@pytest.mark.parametrize('changes',[
    {'resource_delegations':[]},{'resource_delegations':None},
    {'resource_delegations':[dict(COIN_DELEGATION,delegation_version=True)]},
    {'resource_delegations':[dict(COIN_DELEGATION,actor_client_id='other-app')]},
    {'resource_delegations':[dict(COIN_DELEGATION,max_token_lifetime_seconds=600)]},
    {'adapter_contracts':[]},{'scopes_supported':['profile']},
    {'grant_types_supported':['authorization_code','refresh_token']},
])
def test_missing_or_wrong_delegation_does_not_enable_coin(changes):
    client,_=api(document(**changes))
    found=asyncio.run(client.discover(require_introspection=True))
    assert not found.coin_read
    with pytest.raises(AccountError,match='coin_not_connected'):
        client.begin(found,coin=True)
    assert parse_qs(urlsplit(client.begin(found)[1]).query)['scope']==['profile']


def test_coin_consent_is_separate_bound_authorization():
    client,_=api(document())
    found=asyncio.run(client.discover(require_introspection=True))
    assert found.coin_read
    attempt,url=client.begin(found,coin=True)
    query=parse_qs(urlsplit(url).query)
    assert query['scope']==[COIN_SCOPE]
    assert query['audience']==['lazyingart-platform-api']
    assert attempt.scope==COIN_SCOPE
    assert client.begin(found)[0].scope=='profile'


def test_exact_form_exchange_never_sends_profile_token_to_coin():
    client,transport=api(document(),exchange())
    delegated=asyncio.run(client.exchange_coin(TOKENS,IDENTITY))
    request=transport.requests[1]
    fields=parse_qs(request.body.decode())
    assert request.url==ISSUER+'/account/token'
    assert request.headers['Content-Type']=='application/x-www-form-urlencoded'
    assert fields=={
        'grant_type':[EXCHANGE_GRANT],'client_id':['lazyingart-platform-web'],
        'client_secret':[client.config.client_secret],'subject_token':[TOKENS.access_token],
        'subject_token_type':[ACCESS_TOKEN_TYPE],'requested_token_type':[ACCESS_TOKEN_TYPE],
        'audience':['lazyartcoin-read-api'],'scope':['coin.summary.read']}
    assert delegated.subject==IDENTITY.subject and delegated.token=='d'*48
    assert delegated.expires_at==1300
    assert TOKENS.access_token not in repr(delegated)


def test_profile_only_has_no_coin_authority_and_no_network_call():
    client,transport=api()
    with pytest.raises(CoinError,match='permission_required'):
        asyncio.run(client.exchange_coin(replace(TOKENS,scope='profile'),IDENTITY))
    assert not transport.requests


def test_discovery_failure_during_exchange_is_coin_only():
    client,_=api(OSError('synthetic issuer outage'))
    with pytest.raises(CoinError,match='^temporarily_unavailable$'):
        asyncio.run(client.exchange_coin(TOKENS,IDENTITY))


@pytest.mark.parametrize('changes',[
    {'expires_in':True},{'expires_in':301},{'expires_in':0},{'scope':'profile'},
    {'issued_token_type':'refresh_token'},{'refresh_token':'r'*48},
    {'access_token':'bad\nheader'},{'token_type':'other'},
])
def test_bad_exchange_response_never_yields_resource_credential(changes):
    client,_=api(document(),exchange(**changes))
    with pytest.raises(CoinError,match='invalid_summary'):
        asyncio.run(client.exchange_coin(TOKENS,IDENTITY))


@pytest.mark.parametrize('code,state',[(400,'permission_required'),(401,'temporarily_unavailable'),
    (404,'not_connected'),(429,'rate_limited'),(503,'temporarily_unavailable')])
def test_exchange_errors_do_not_retry_or_expose_response(code,state):
    client,transport=api(document(),SimpleNamespace(code=code,body=b'secret failure'))
    with pytest.raises(CoinError,match='^'+state+'$'):
        asyncio.run(client.exchange_coin(TOKENS,IDENTITY))
    assert len(transport.requests)==2


def test_delegated_lifetime_cannot_outlive_local_parent():
    client,_=api(document(),exchange())
    delegated=asyncio.run(client.exchange_coin(replace(TOKENS,expires_at=1100),IDENTITY))
    assert delegated.expires_at==1100


def test_scope_cannot_expand_on_ordinary_exchange_or_refresh():
    client,_=api()
    with pytest.raises(AccountError):
        client._tokens(token_response(scope=COIN_SCOPE))
    assert client._tokens(token_response(scope=COIN_SCOPE),expected_scope=COIN_SCOPE).scope==COIN_SCOPE
    assert client._tokens(token_response(),expected_scope=COIN_SCOPE,allow_reduced_scope=True).scope=='profile'
    for scope in ({},[],None,'profile admin'):
        with pytest.raises(AccountError):
            client._tokens(token_response(scope=scope))
