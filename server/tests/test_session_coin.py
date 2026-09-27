import asyncio
from dataclasses import replace
from unittest.mock import AsyncMock

import pytest

from server.account_client import AccountError, COIN_SCOPE, Discovery
from server.coin_client import CoinError, ReadCredential
from test_account_sessions import setup
from test_coin_client import sample


def connected(setup):
    setup.client.discover.return_value=Discovery(setup.identity.issuer,('password',),True)
    evidence=replace(setup.client.introspect.return_value,scope=COIN_SCOPE)
    setup.client.introspect.return_value=evidence
    opaque=setup.persistence.create(setup.identity,replace(setup.tokens,scope=COIN_SCOPE))
    setup.client.exchange_coin=AsyncMock(return_value=ReadCredential(setup.identity.issuer,
        setup.identity.subject,'d'*48,1000,1300))
    data=sample()
    data['account']={'issuer':setup.identity.issuer,'subject':setup.identity.subject}
    reader=AsyncMock()
    reader.read.return_value=data
    return opaque,reader,evidence


def test_signed_in_read_is_bound_before_and_after_io(setup):
    opaque,reader,_=connected(setup)
    result=asyncio.run(setup.service.coin_summary(opaque,reader,setup.identity))
    assert result['state']=='available'
    assert result['summary']['on_chain']['lac_units']=='500000000000000000000'
    assert setup.client.introspect.await_count==2
    assert reader.read.await_args.args[0].token=='d'*48


def test_no_consent_never_calls_resource_or_exchange(setup):
    setup.client.discover.return_value=Discovery(setup.identity.issuer,('password',),True)
    opaque=setup.persistence.create(setup.identity,setup.tokens)
    reader=AsyncMock()
    result=asyncio.run(setup.service.coin_summary(opaque,reader,setup.identity))
    assert result=={'state':'permission_required','summary':None}
    reader.read.assert_not_awaited()


def test_disabled_resource_discovery_does_not_offer_consent(setup):
    opaque,reader,_=connected(setup)
    setup.client.discover.return_value=Discovery(setup.identity.issuer,('password',),False)
    assert asyncio.run(setup.service.coin_summary(opaque,reader,setup.identity)) == {'state':'not_connected','summary':None}
    reader.read.assert_not_awaited()


def test_discovery_outage_keeps_profile_session(setup):
    opaque,reader,_=connected(setup)
    setup.client.discover.side_effect=AccountError('account_service_unavailable')
    assert asyncio.run(setup.service.coin_summary(opaque,reader,setup.identity)) == {'state':'temporarily_unavailable','summary':None}
    assert setup.persistence.read(opaque)


def test_logout_in_another_worker_discards_pending_summary(setup):
    opaque,reader,_=connected(setup)
    original=reader.read.return_value
    async def read(*_):
        setup.persistence.remove(opaque)
        return original
    reader.read.side_effect=read
    with pytest.raises(AccountError,match='account_authorization_required'):
        asyncio.run(setup.service.coin_summary(opaque,reader,setup.identity))


def test_consent_revoked_during_read_discards_quantities(setup):
    opaque,reader,evidence=connected(setup)
    setup.client.introspect.side_effect=[evidence,replace(evidence,scope='profile')]
    result=asyncio.run(setup.service.coin_summary(opaque,reader,setup.identity))
    assert result=={'state':'permission_required','summary':None}


def test_changed_identity_never_fetches_a_different_user(setup):
    opaque,reader,_=connected(setup)
    with pytest.raises(AccountError,match='invalid_account_identity'):
        asyncio.run(setup.service.coin_summary(opaque,reader,replace(setup.identity,subject='la_'+'b'*32)))
    reader.read.assert_not_awaited()


def test_wrong_summary_owner_never_reaches_response(setup):
    opaque,reader,_=connected(setup)
    reader.read.return_value['account']['subject']='la_'+'b'*32
    result=asyncio.run(setup.service.coin_summary(opaque,reader,setup.identity))
    assert result=={'state':'temporarily_unavailable','summary':None}


@pytest.mark.parametrize('state',['temporarily_unavailable','rate_limited','not_connected','permission_required','authorization_required','arbitrary secret'])
def test_resource_outage_or_denial_is_not_zero_or_raw_error(setup,state):
    opaque,reader,_=connected(setup)
    reader.read.side_effect=CoinError(state)
    result=asyncio.run(setup.service.coin_summary(opaque,reader,setup.identity))
    assert result['summary'] is None
    assert 'arbitrary secret' not in str(result)
    assert setup.persistence.read(opaque)


def test_profile_logout_during_introspection_does_not_return_identity(setup):
    opaque=setup.persistence.create(setup.identity,setup.tokens)
    evidence=setup.client.introspect.return_value
    async def revoked(_):
        setup.persistence.remove(opaque)
        return evidence
    setup.client.introspect.side_effect=revoked
    with pytest.raises(AccountError):
        asyncio.run(setup.service.identity(opaque))
