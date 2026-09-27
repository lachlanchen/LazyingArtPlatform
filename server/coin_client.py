"""Staged Coin summary consumer; no issuer exchange or production wiring.

Implements Coin's source-tested summary-v1 contract (40c78b3). Only a future
qualified central delegation adapter may supply ReadCredential. Ordinary
Platform profile credentials must never be passed to this client.
"""
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
import html
import json
import re
import time

import tornado.httpclient

from server.account_client import credential

ENDPOINT = 'https://coin.lazying.art/api/integrations/v1/me'
TOKEN = '0x56E140d1ce7bFf0a7B83E5a778829111f069326E'
BUCKETS = ('awaiting_delivery_units', 'unresolved_attempt_units',
           'submitted_unconfirmed_units', 'confirmed_units')


class CoinError(ValueError):
    """Safe state, never contains an upstream response or credential."""


def require(condition):
    if not condition:
        raise CoinError('invalid_summary')


def fields(value, names):
    require(isinstance(value, dict) and set(value) == set(names.split()))
    return value


def integer(value, minimum=0):
    require(type(value) is int and minimum <= value <= 10**12)


def quantity(value):
    require(isinstance(value, str) and re.fullmatch(r'0|[1-9][0-9]{0,119}', value) is not None)
    return value


def text(value, limit=2048):
    require(isinstance(value, str) and 0 < len(value) <= limit and not re.search(r'[\x00-\x1f]', value))


def address(value):
    require(isinstance(value, str) and re.fullmatch(r'0x[0-9a-fA-F]{40}', value) is not None)


def tx_hash(value):
    require(isinstance(value, str) and re.fullmatch(r'0x[0-9a-fA-F]{64}', value) is not None)


def validate_summary(data, identity):
    """Validate full response and bind it to the initiating server identity."""
    fields(data, 'schema_version observed_at account asset account_link wallet on_chain grants credits')
    require(type(data['schema_version']) is int and data['schema_version'] == 1)
    fields(data['account'], 'issuer subject')
    require(data['account'] == {'issuer': identity.issuer, 'subject': identity.subject})
    require(isinstance(data['observed_at'], str) and len(data['observed_at']) <= 40)
    try:
        observed = datetime.fromisoformat(data['observed_at'].replace('Z', '+00:00'))
        require(observed.utcoffset() is not None and observed.utcoffset().total_seconds() == 0)
    except (ValueError, TypeError):
        raise CoinError('invalid_summary') from None
    asset = fields(data['asset'], 'chain_id token_address symbol decimals')
    require(type(asset['chain_id']) is int and asset['chain_id'] == 1)
    require(type(asset['decimals']) is int and asset['decimals'] == 18)
    require(asset['token_address'] == TOKEN and asset['symbol'] == 'LAC')
    link = fields(data['account_link'], 'state')['state']
    require(link in ('linked', 'link_required', 'profile_deleted'))
    wallet = fields(data['wallet'], 'state address verified_at')
    chain = fields(data['on_chain'], 'state lac_units eth_wei block_number block_hash finality')
    grants = fields(data['grants'], 'state items totals total_count recent_limit has_more')
    require(type(grants['recent_limit']) is int and grants['recent_limit'] == 20)
    require(data['credits'] == {'source':'EchoMind', 'state':'adapter_not_configured', 'balance':None, 'redeemable':False})
    require(type(data['credits']['redeemable']) is bool)

    if link != 'linked':
        require(wallet == {'state':link, 'address':None, 'verified_at':None})
        require(chain == dict(state=link, lac_units=None, eth_wei=None, block_number=None, block_hash=None, finality=None))
        require(grants == dict(state=link, items=None, totals=None, total_count=None, recent_limit=20, has_more=None))
        return data

    require(wallet['state'] in ('linked', 'not_linked'))
    if wallet['state'] == 'linked':
        address(wallet['address'])
        # The Coin owner may retain a wallet without a historical proof time.
        if wallet['verified_at'] is not None:
            integer(wallet['verified_at'])
        require(chain['state'] in ('available', 'temporarily_unavailable'))
    else:
        require(wallet['address'] is None and wallet['verified_at'] is None)
        require(chain['state'] == 'not_linked')
    if chain['state'] == 'available':
        for name in ('lac_units', 'eth_wei', 'block_number'):
            quantity(chain[name])
        tx_hash(chain['block_hash'])
        require(chain['finality'] == 'latest')
    else:
        require(all(chain[name] is None for name in ('lac_units','eth_wei','block_number','block_hash','finality')))

    require(grants['state'] == 'available')
    fields(grants['totals'], ' '.join(BUCKETS))
    for value in grants['totals'].values():
        quantity(value)
    integer(grants['total_count'])
    require(type(grants['has_more']) is bool)
    require(isinstance(grants['items'], list) and len(grants['items']) == min(20, grants['total_count']))
    require(grants['has_more'] == (grants['total_count'] > 20))
    seen = set()
    for item in grants['items']:
        fields(item, 'id campaign_id title address created_at state amount_units tx_hash tier_held delivery_enabled')
        for name in ('id', 'campaign_id', 'title'):
            text(item[name])
        require(item['id'] not in seen)
        seen.add(item['id'])
        address(item['address'])
        integer(item['created_at'])
        require(item['state'] in ('registered','awaiting_delivery','reconciliation_required','submitted_unconfirmed','confirmed'))
        for name in ('tier_held', 'delivery_enabled'):
            require(item[name] is None or type(item[name]) is bool)
        if item['state'] == 'registered':
            require(item['amount_units'] is None)
        else:
            quantity(item['amount_units'])
        if item['state'] in ('submitted_unconfirmed','confirmed'):
            tx_hash(item['tx_hash'])
        else:
            require(item['tx_hash'] is None)
    return data


@dataclass(frozen=True)
class ReadCredential:
    issuer: str
    subject: str
    token: str = field(repr=False)
    issued_at: int
    expires_at: int
    audience: str = 'lazyartcoin-read-api'
    actor: str = 'lazyingart-platform-web'
    scope: str = 'coin.summary.read'
    version: int = 1

    def validate(self, identity, now):
        # This binding is defensive validation, not self-issued authorization:
        # Coin independently introspects every supplied opaque resource token.
        if (self.issuer != identity.issuer or self.subject != identity.subject
                or self.audience != 'lazyartcoin-read-api'
                or self.actor != 'lazyingart-platform-web' or self.scope != 'coin.summary.read'
                or type(self.version) is not int or self.version != 1
                or type(self.issued_at) is not int or type(self.expires_at) is not int
                or not 0 < self.expires_at - self.issued_at <= 300
                or not self.issued_at <= now < self.expires_at):
            raise CoinError('delegation_required')
        try:
            credential(self.token)
        except ValueError:
            raise CoinError('delegation_required') from None


class CoinSummaryClient:
    def __init__(self, *, http=None, clock=time.time):
        self.clock = clock
        self._owns_http = http is None
        self.http = http or tornado.httpclient.AsyncHTTPClient(force_instance=True, max_body_size=65536)

    def close(self):
        if self._owns_http:
            self.http.close()

    async def read(self, delegated, identity):
        if not isinstance(delegated, ReadCredential):
            raise CoinError('delegation_required')
        delegated.validate(identity, self.clock())
        try:
            response = await self.http.fetch(ENDPOINT, method='GET',
                headers={'Accept':'application/json', 'X-Lac-Read-Token':delegated.token},
                follow_redirects=False, validate_cert=True, request_timeout=15,
                connect_timeout=5, raise_error=False)
        except (tornado.httpclient.HTTPClientError, OSError, asyncio.TimeoutError):
            raise CoinError('temporarily_unavailable') from None
        # No automatic refresh, retry, redirect, alternate route or legacy token.
        states = {401:'authorization_required',403:'permission_required',
                  404:'not_connected',429:'rate_limited',503:'temporarily_unavailable'}
        if response.code != 200:
            raise CoinError(states.get(response.code, 'temporarily_unavailable'))
        delegated.validate(identity, self.clock())
        if (len(response.body) > 65536 or response.headers.get('Content-Type','').split(';')[0].strip() != 'application/json'):
            raise CoinError('invalid_summary')
        try:
            data = json.loads(response.body)
        except (ValueError, UnicodeError):
            raise CoinError('invalid_summary') from None
        return validate_summary(data, identity)


def format_units(value):
    """Exact base-10 formatting, including quantities beyond IEEE-754 precision."""
    digits = quantity(value).zfill(19)
    whole, fraction = digits[:-18], digits[-18:].rstrip('0')
    return whole + ('.' + fraction if fraction else '')


def render_summary(data, identity):
    """Private server-rendered view; never combines balances with grant totals."""
    validate_summary(data, identity)
    out = ['<section aria-label="Your LazyingArt coins"><h2>Your LazyingArt coins</h2>']
    link = data['account_link']['state']
    if link != 'linked':
        message = 'Connect your Coin profile to see its summary.' if link == 'link_required' else 'Your Coin profile has been deleted.'
        out.append('<p>'+message+'</p>')
    else:
        chain = data['on_chain']
        if data['wallet']['state'] == 'linked':
            out.append('<p class="small">Linked wallet: <code>'+html.escape(data['wallet']['address'])+'</code></p>')
        if chain['state'] == 'available':
            out.append('<p>Wallet balance: <strong>'+format_units(chain['lac_units'])+' LAC</strong></p>')
            out.append('<p>ETH for gas: '+format_units(chain['eth_wei'])+' ETH. Latest block observation, not final settlement.</p>')
        else:
            out.append('<p>'+('No receiving wallet is linked.' if chain['state'] == 'not_linked' else 'Wallet balance is temporarily unavailable.')+'</p>')
        out.append('<h3>Grants — separate from your wallet balance</h3><dl>')
        labels = ('Awaiting delivery','Transfer under reconciliation','Submitted, not confirmed','Confirmed historical receipts')
        for name, label in zip(BUCKETS, labels):
            out.append('<dt>'+label+'</dt><dd>'+format_units(data['grants']['totals'][name])+' LAC</dd>')
        out.append('</dl><p>Historical receipts are not an additional spendable balance.</p>')
        if data['grants']['items']:
            out.append('<ul>')
            for item in data['grants']['items']:
                amount = 'Registration only' if item['amount_units'] is None else format_units(item['amount_units'])+' LAC'
                out.append('<li>'+html.escape(item['title'])+' — '+amount+'; '+html.escape(item['state'].replace('_',' '))+'.</li>')
            out.append('</ul>')
        if data['grants']['has_more']:
            out.append('<p>Showing the newest 20 grants; totals include all your grants.</p>')
    out.append('<p class="small">Observed '+html.escape(data['observed_at'])+'</p>')
    out.append('<p><a href="https://coin.lazying.art/">Open Coin</a></p></section>')
    return ''.join(out)
