"""Synthetic Coin contract tests; no token exchange, real account or network."""
import asyncio
from dataclasses import replace
import json
from types import SimpleNamespace

import pytest
from tornado.httpclient import HTTPRequest

from server.account_client import Identity, Credentials
from server.coin_client import (BUCKETS, ENDPOINT, TOKEN, CoinError,
    CoinSummaryClient, ReadCredential, format_units, render_summary, validate_summary)

IDENTITY = Identity('https://accounts.example.test','la_'+'a'*32,'Fixture','lazyingart-platform-web')
AUTH = ReadCredential(IDENTITY.issuer,IDENTITY.subject,'synthetic_resource_'+'a'*48,1000,1300)


def sample():
    return {
        'schema_version':1, 'observed_at':'2026-09-27T00:00:00+00:00',
        'account':{'issuer':IDENTITY.issuer,'subject':IDENTITY.subject},
        'asset':{'chain_id':1,'token_address':TOKEN,'symbol':'LAC','decimals':18},
        'account_link':{'state':'linked'},
        'wallet':{'state':'linked','address':'0x'+'1'*40,'verified_at':1700000000},
        'on_chain':{'state':'available','lac_units':'500000000000000000000','eth_wei':'0',
                    'block_number':'12345678','block_hash':'0x'+'b'*64,'finality':'latest'},
        'grants':{'state':'available','items':[{
            'id':'example-grant','campaign_id':'example-campaign','title':'Synthetic campaign',
            'address':'0x'+'1'*40,'created_at':1700000001,'state':'awaiting_delivery',
            'amount_units':'1000000000000000000000','tx_hash':None,
            'tier_held':False,'delivery_enabled':False}],
            'totals':dict(zip(BUCKETS,('1000000000000000000000','0','0','0'))),
            'total_count':1,'recent_limit':20,'has_more':False},
        'credits':{'source':'EchoMind','state':'adapter_not_configured','balance':None,'redeemable':False}}


class Transport:
    def __init__(self, data=None, status=200, content_type='application/json', action=None):
        self.data, self.status, self.content_type = data, status, content_type
        self.action, self.requests = action, []

    async def fetch(self, url, **kwargs):
        assert kwargs.pop('raise_error') is False
        request = HTTPRequest(url,**kwargs)
        self.requests.append(request)
        if self.action:
            self.action()
        return SimpleNamespace(code=self.status,body=json.dumps(self.data).encode(),
                               headers={'Content-Type':self.content_type})


def test_only_delegated_header_to_exact_resource_and_no_redirect():
    transport=Transport(sample())
    api=CoinSummaryClient(http=transport,clock=lambda:1001)
    assert asyncio.run(api.read(AUTH,IDENTITY))==sample()
    req=transport.requests[0]
    assert req.url==ENDPOINT and req.method=='GET' and req.body is None
    assert dict(req.headers)=={'Accept':'application/json','X-Lac-Read-Token':AUTH.token}
    assert not req.follow_redirects and req.validate_cert
    assert req.connect_timeout==5 and req.request_timeout==15
    assert AUTH.token not in repr(AUTH)


@pytest.mark.parametrize('changes',[
    {'issuer':'https://wrong.example'},{'subject':'la_'+'b'*32},
    {'audience':'lazyingart-platform-api'},{'scope':'profile'},{'actor':'another-app'},
    {'version':True},{'version':2},{'expires_at':1001},{'expires_at':1301},
    {'issued_at':True},{'issued_at':1002},{'token':'bad\r\nheader'},
])
def test_delegation_binding_rejected_before_network(changes):
    transport=Transport(sample())
    with pytest.raises(CoinError,match='delegation_required'):
        asyncio.run(CoinSummaryClient(http=transport,clock=lambda:1001).read(replace(AUTH,**changes),IDENTITY))
    assert not transport.requests


def test_profile_token_object_is_never_a_resource_credential():
    transport=Transport(sample())
    with pytest.raises(CoinError,match='delegation_required'):
        asyncio.run(CoinSummaryClient(http=transport).read(Credentials('a'*48,'b'*48,1200),IDENTITY))
    assert not transport.requests


def test_expiry_during_read_discards_result():
    clock=[1001]
    transport=Transport(sample(),action=lambda:clock.__setitem__(0,1300))
    with pytest.raises(CoinError,match='delegation_required'):
        asyncio.run(CoinSummaryClient(http=transport,clock=lambda:clock[0]).read(AUTH,IDENTITY))


@pytest.mark.parametrize('code,state',[(401,'authorization_required'),(403,'permission_required'),
    (404,'not_connected'),(429,'rate_limited'),(503,'temporarily_unavailable'),
    (302,'temporarily_unavailable'),(502,'temporarily_unavailable')])
def test_errors_are_safe_without_retry_or_zero(code,state):
    transport=Transport({'secret':'must not escape'},status=code)
    with pytest.raises(CoinError,match='^'+state+'$'):
        asyncio.run(CoinSummaryClient(http=transport,clock=lambda:1001).read(AUTH,IDENTITY))
    assert len(transport.requests)==1


@pytest.mark.parametrize('content_type',['text/html','text/plain',''])
def test_non_json_success_rejected(content_type):
    with pytest.raises(CoinError,match='invalid_summary'):
        asyncio.run(CoinSummaryClient(http=Transport(sample(),content_type=content_type),clock=lambda:1001).read(AUTH,IDENTITY))


@pytest.mark.parametrize('path,value',[
    (('account','subject'),'la_'+'b'*32),(('account','issuer'),'https://wrong.example'),
    (('asset','token_address'),'0x'+'0'*40),(('asset','chain_id'),True),
    (('asset','decimals'),6),(('on_chain','lac_units'),500),
    (('on_chain','lac_units'),'5e20'),(('on_chain','lac_units'),'-1'),
    (('on_chain','lac_units'),'01'),(('on_chain','finality'),'finalized'),
    (('on_chain','block_hash'),'garbage'),(('grants','has_more'),True),
    (('grants','total_count'),0),(('grants','recent_limit'),21),
    (('credits','balance'),'0'),(('credits','redeemable'),0),
])
def test_invalid_or_cross_account_summaries_rejected(path,value):
    data=sample(); data[path[0]][path[1]]=value
    with pytest.raises(CoinError,match='invalid_summary'):
        validate_summary(data,IDENTITY)


@pytest.mark.parametrize('state',['link_required','profile_deleted'])
def test_unlinked_and_deleted_never_show_fake_zero(state):
    data=sample()
    data['account_link']['state']=state
    data['wallet']=dict(state=state,address=None,verified_at=None)
    data['on_chain']=dict(state=state,lac_units=None,eth_wei=None,block_number=None,block_hash=None,finality=None)
    data['grants']=dict(state=state,items=None,totals=None,total_count=None,recent_limit=20,has_more=None)
    rendered=render_summary(data,IDENTITY)
    assert '0 LAC' not in rendered and 'Wallet balance:' not in rendered
    data['on_chain']['lac_units']='0'
    with pytest.raises(CoinError): validate_summary(data,IDENTITY)


def test_rpc_outage_keeps_separate_grants_and_null_chain():
    data=sample()
    data['on_chain']=dict(state='temporarily_unavailable',lac_units=None,eth_wei=None,block_number=None,block_hash=None,finality=None)
    rendered=render_summary(data,IDENTITY)
    assert 'Wallet balance is temporarily unavailable' in rendered
    assert '1000 LAC' in rendered and 'Wallet balance: <strong>0' not in rendered


def test_exact_formatting_and_no_balance_grant_addition():
    data=sample(); data['grants']['items'][0]['title']='<img src=x onerror=alert(1)>'
    rendered=render_summary(data,IDENTITY)
    assert '<strong>500 LAC</strong>' in rendered and '1000 LAC' in rendered
    assert '1500 LAC' not in rendered and '<img' not in rendered and '&lt;img' in rendered
    assert format_units('9007199254740993000000000000000001')=='9007199254740993.000000000000000001'
    assert format_units('1')=='0.000000000000000001' and format_units('0')=='0'


def test_empty_linked_grants_is_actual_zero_not_unavailable():
    data=sample(); data['grants'].update(items=[],total_count=0,totals=dict.fromkeys(BUCKETS,'0'))
    assert validate_summary(data,IDENTITY)['grants']['items']==[]


def test_extra_fields_and_unbounded_body_rejected():
    data=sample(); data['admin_secret']='unexpected'
    with pytest.raises(CoinError): validate_summary(data,IDENTITY)
    with pytest.raises(CoinError):
        asyncio.run(CoinSummaryClient(http=Transport('x'*65537),clock=lambda:1001).read(AUTH,IDENTITY))
