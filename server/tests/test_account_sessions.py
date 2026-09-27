# Adapted from the owner's LazyingArtCoin account consumer at b3e7ebf.
# Profile-only Platform preparation; no Coin ledger or provider authority.
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from cryptography.fernet import Fernet
import pytest

from server.account_client import (AccountClient, AccountError, ClientConfiguration,
    Credentials, Discovery, Identity, IdentityEvidence)
from server.account_sessions import AccountSessions, SessionStore
from server.storage import Database


@pytest.fixture
def setup(tmp_path):
    now = [1000]
    config = ClientConfiguration('https://accounts.example.test', 'platform-web', 'platform-api',
                                'https://platform.lazying.art/api/account/callback', 'synthetic-client-secret')
    client = SimpleNamespace(config=config, clock=lambda: now[0])
    client.begin = lambda discovery, **kwargs: AccountClient.begin(client, discovery, **kwargs)
    client.discover = AsyncMock(return_value=Discovery(config.issuer, ('password',)))
    identity = Identity(config.issuer, 'la_' + 'a' * 32, 'Member', config.client_id)
    evidence = IdentityEvidence(identity, True, 900)
    tokens = Credentials('a' * 48, 'r' * 48, 1600)
    client.complete = AsyncMock(return_value=tokens)
    client.introspect = AsyncMock(return_value=evidence)
    client.revoke = AsyncMock()
    client.refresh = AsyncMock(return_value=Credentials('b' * 48, 's' * 48, 1600))
    store = Database(tmp_path / 'test.sqlite3')
    key = Fernet.generate_key()
    persistence = SessionStore(store, key, client)
    persistence.install_schema()
    service = AccountSessions(client, persistence)
    return SimpleNamespace(now=now, client=client, identity=identity, tokens=tokens, store=store,
        key=key, persistence=persistence, service=service)


def test_encrypted_storage_and_bound_one_use_attempt(setup):
    attempt, url = setup.client.begin(Discovery(setup.client.config.issuer, ('password',)))
    browser = 'browser_' + 'b' * 40
    setup.persistence.save_attempt(attempt, browser)
    opaque = setup.persistence.create(setup.identity, setup.tokens)
    with setup.store.db() as db:
        attempts = list(db.execute('SELECT * FROM account_attempts'))
        sessions = list(db.execute('SELECT * FROM platform_account_sessions'))
        serialized = repr([tuple(row) for row in attempts + sessions])
    for secret in (attempt.verifier, attempt.state, browser, opaque, setup.tokens.access_token, setup.tokens.refresh_token):
        assert secret not in serialized
    with pytest.raises(AccountError):
        setup.persistence.consume_attempt(attempt.state, 'wrong_' + 'b' * 40)
    assert setup.persistence.consume_attempt(attempt.state, browser).verifier == attempt.verifier
    with pytest.raises(AccountError):
        setup.persistence.consume_attempt(attempt.state, browser)
    _, read = setup.persistence.read(opaque)
    assert read == setup.tokens


def test_configuration_and_encryption_key_isolate_sessions(setup):
    opaque = setup.persistence.create(setup.identity, setup.tokens)
    other = SessionStore(setup.store, Fernet.generate_key(), setup.client)
    with pytest.raises(AccountError, match='reconnect'):
        other.read(opaque)
    other.binding = 'different-client-binding'
    with pytest.raises(AccountError, match='authorization_required'):
        other.read(opaque)


def test_refresh_generation_cas_rejects_stale_worker(setup):
    opaque = setup.persistence.create(setup.identity, setup.tokens)
    row, _ = setup.persistence.read(opaque)
    setup.persistence.claim_refresh(opaque, row['payload'])
    setup.persistence.finish_refresh(opaque, Credentials('b' * 48, 's' * 48, 1600))
    with pytest.raises(AccountError, match='in_progress'):
        setup.persistence.claim_refresh(opaque, row['payload'])


def test_crashed_refresh_requires_reconnect_without_reusing_old_token(setup):
    opaque = setup.persistence.create(setup.identity, setup.tokens)
    row, _ = setup.persistence.read(opaque)
    setup.persistence.claim_refresh(opaque, row['payload'])
    with pytest.raises(AccountError, match='in_progress'):
        setup.persistence.read(opaque)
    setup.now[0] += 31
    with pytest.raises(AccountError, match='reconnect'):
        setup.persistence.read(opaque)
    setup.client.refresh.assert_not_called()
    with setup.store.db() as db:
        assert db.execute('SELECT payload FROM platform_account_sessions').fetchone()[0] is None


def test_parallel_refresh_only_sends_one_rotating_credential(setup):
    async def scenario():
        opaque = setup.persistence.create(setup.identity, Credentials('a' * 48, 'r' * 48, 1001))
        results = await asyncio.gather(*(setup.service.identity(opaque) for _ in range(8)))
        assert all(evidence.identity == setup.identity for evidence in results)
        assert setup.client.refresh.await_count == 1
        assert setup.client.introspect.await_count == 8
    asyncio.run(scenario())


def test_outage_preserves_session_but_revocation_invalidates_it(setup):
    async def scenario():
        opaque = setup.persistence.create(setup.identity, setup.tokens)
        setup.client.introspect.side_effect = AccountError('account_service_unavailable')
        with pytest.raises(AccountError, match='unavailable'):
            await setup.service.identity(opaque)
        assert setup.persistence.read(opaque)[1] == setup.tokens
        setup.client.introspect.side_effect = AccountError('account_authorization_required')
        with pytest.raises(AccountError, match='authorization_required'):
            await setup.service.identity(opaque)
        with pytest.raises(AccountError, match='reconnect'):
            setup.persistence.read(opaque)
    asyncio.run(scenario())


def test_lost_refresh_response_is_durable_failure(setup):
    async def scenario():
        opaque = setup.persistence.create(setup.identity, Credentials('a' * 48, 'r' * 48, 1001))
        setup.client.refresh.side_effect = AccountError('account_service_unavailable')
        with pytest.raises(AccountError, match='unavailable'):
            await setup.service.identity(opaque)
        restarted = AccountSessions(setup.client, SessionStore(setup.store, setup.key, setup.client))
        with pytest.raises(AccountError, match='reconnect'):
            await restarted.identity(opaque)
        assert setup.client.refresh.await_count == 1
    asyncio.run(scenario())


def test_cross_worker_logout_cannot_be_undone_by_inflight_refresh(setup):
    async def scenario():
        opaque = setup.persistence.create(setup.identity, Credentials('a' * 48, 'r' * 48, 1001))
        started, release = asyncio.Event(), asyncio.Event()
        async def refresh(tokens):
            started.set()
            await release.wait()
            return Credentials('b' * 48, 's' * 48, 1600)
        setup.client.refresh.side_effect = refresh
        pending = asyncio.create_task(setup.service.identity(opaque))
        await started.wait()
        other = AccountSessions(setup.client, setup.persistence)
        await other.logout(opaque)
        release.set()
        with pytest.raises(AccountError):
            await pending
        with pytest.raises(AccountError, match='authorization_required'):
            setup.persistence.read(opaque)
        setup.client.revoke.assert_awaited_once()
    asyncio.run(scenario())


def test_logout_survives_revocation_service_outage(setup):
    async def scenario():
        opaque = setup.persistence.create(setup.identity, setup.tokens)
        setup.client.revoke.side_effect = AccountError('account_service_unavailable')
        assert await setup.service.logout(opaque) is False
        with pytest.raises(AccountError):
            setup.persistence.read(opaque)
    asyncio.run(scenario())
