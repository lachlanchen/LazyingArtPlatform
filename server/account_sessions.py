# Adapted from the owner's LazyingArtCoin account consumer at b3e7ebf.
# Profile-only Platform preparation; no Coin ledger or provider authority.
"""Protected, app-local web sessions for the opt-in central account adapter."""

import asyncio
from dataclasses import asdict
import hashlib
import json
import re
import secrets
import weakref

from cryptography.fernet import Fernet, InvalidToken

from server.account_client import AccountClient, AccountError, AuthorizationAttempt, Credentials


def digest(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{32,256}', value):
        raise AccountError('account_authorization_required')
    return hashlib.sha256(value.encode()).hexdigest()


class SessionStore:
    def __init__(self, store, key: bytes, client: AccountClient):
        self.store, self.client, self.cipher = store, client, Fernet(key)
        config = client.config
        self.binding = hashlib.sha256(json.dumps([config.issuer, config.client_id, config.audience, config.redirect_uri]).encode()).hexdigest()

    def install_schema(self):
        """Explicit staging/operator migration; construction never migrates."""
        with self.store.db() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS account_attempts (
                    state_digest TEXT PRIMARY KEY, browser_digest TEXT NOT NULL,
                    binding TEXT NOT NULL, payload BLOB NOT NULL, expires INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS platform_account_sessions (
                    digest TEXT PRIMARY KEY, binding TEXT NOT NULL, issuer TEXT NOT NULL,
                    subject TEXT NOT NULL, payload BLOB, status TEXT NOT NULL,
                    refresh_started INTEGER, expires INTEGER NOT NULL);
            ''')

    def seal(self, value):
        return self.cipher.encrypt(json.dumps(value).encode())

    def open(self, value):
        try:
            return json.loads(self.cipher.decrypt(value))
        except (InvalidToken, ValueError, TypeError):
            raise AccountError('account_reconnect_required') from None

    def save_attempt(self, attempt, browser):
        with self.store.db() as db:
            now = int(self.client.clock())
            db.execute('DELETE FROM account_attempts WHERE expires<=?', (now,))
            db.execute('DELETE FROM platform_account_sessions WHERE expires<=?', (now,))
            db.execute('INSERT INTO account_attempts VALUES (?,?,?,?,?)',
                       (digest(attempt.state), digest(browser), self.binding, self.seal(asdict(attempt)), int(attempt.expires_at)))

    def consume_attempt(self, state, browser):
        with self.store.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT * FROM account_attempts WHERE state_digest=? AND browser_digest=? AND binding=? AND expires>?',
                             (digest(state), digest(browser), self.binding, int(self.client.clock()))).fetchone()
            if not row:
                raise AccountError('authorization_attempt_expired')
            db.execute('DELETE FROM account_attempts WHERE state_digest=?', (digest(state),))
            return AuthorizationAttempt(**self.open(row['payload']))

    def create(self, identity, tokens):
        opaque = secrets.token_urlsafe(48)
        with self.store.db() as db:
            db.execute('INSERT INTO platform_account_sessions VALUES (?,?,?,?,?,?,NULL,?)',
                       (digest(opaque), self.binding, identity.issuer, identity.subject,
                        self.seal(asdict(tokens)), 'active', int(self.client.clock()) + 30 * 86400))
        return opaque

    def read(self, opaque):
        with self.store.db() as db:
            row = db.execute('SELECT * FROM platform_account_sessions WHERE digest=? AND binding=? AND expires>?',
                             (digest(opaque), self.binding, int(self.client.clock()))).fetchone()
        if not row:
            raise AccountError('account_authorization_required')
        if row['status'] == 'refreshing':
            if row['refresh_started'] + 30 > self.client.clock():
                raise AccountError('account_refresh_in_progress')
            self.invalidate(opaque)
            raise AccountError('account_reconnect_required')
        if row['status'] != 'active':
            raise AccountError('account_reconnect_required')
        return row, Credentials(**self.open(row['payload']))

    def claim_refresh(self, opaque, expected_payload):
        with self.store.db() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute("UPDATE platform_account_sessions SET status='refreshing',refresh_started=? WHERE digest=? AND binding=? AND status='active' AND payload=?",
                          (int(self.client.clock()), digest(opaque), self.binding, expected_payload)).rowcount != 1:
                raise AccountError('account_refresh_in_progress')

    def finish_refresh(self, opaque, tokens):
        with self.store.db() as db:
            if db.execute("UPDATE platform_account_sessions SET payload=?,status='active',refresh_started=NULL WHERE digest=? AND binding=? AND status='refreshing' AND expires>?",
                          (self.seal(asdict(tokens)), digest(opaque), self.binding, int(self.client.clock()))).rowcount != 1:
                raise AccountError('account_reconnect_required')

    def invalidate(self, opaque):
        with self.store.db() as db:
            db.execute("UPDATE platform_account_sessions SET status='reconnect',payload=NULL WHERE digest=? AND binding=?", (digest(opaque), self.binding))

    def remove(self, opaque):
        with self.store.db() as db:
            db.execute('DELETE FROM platform_account_sessions WHERE digest=? AND binding=?', (digest(opaque), self.binding))


class AccountSessions:
    def __init__(self, client: AccountClient, persistence: SessionStore):
        self.client, self.persistence = client, persistence
        self._locks = weakref.WeakValueDictionary()

    def lock(self, opaque):
        key = digest(opaque)
        lock = self._locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[key] = lock
        return lock

    async def start(self):
        found = await self.client.discover(require_introspection=True)
        attempt, url = self.client.begin(found)
        browser = secrets.token_urlsafe(32)
        await asyncio.to_thread(self.persistence.save_attempt, attempt, browser)
        return browser, url

    async def complete(self, state, browser, callback):
        attempt = await asyncio.to_thread(self.persistence.consume_attempt, state, browser)
        tokens = await self.client.complete(attempt, callback)
        try:
            evidence = await self.client.introspect(tokens)
            return await asyncio.to_thread(self.persistence.create, evidence.identity, tokens)
        except BaseException:
            try:
                await self.client.revoke(tokens)
            except AccountError:
                pass
            raise

    async def identity(self, opaque):
        async with self.lock(opaque):
            row, tokens = await asyncio.to_thread(self.persistence.read, opaque)
            if tokens.expires_at - self.client.clock() <= 30:
                await asyncio.to_thread(self.persistence.claim_refresh, opaque, row['payload'])
                refreshed = None
                try:
                    tokens = refreshed = await self.client.refresh(tokens)
                    await asyncio.to_thread(self.persistence.finish_refresh, opaque, tokens)
                except BaseException:
                    await asyncio.to_thread(self.persistence.invalidate, opaque)
                    if refreshed:
                        try:
                            await self.client.revoke(refreshed)
                        except AccountError:
                            pass
                    raise
            try:
                evidence = await self.client.introspect(tokens)
                if (evidence.identity.issuer, evidence.identity.subject) != (row['issuer'], row['subject']):
                    raise AccountError('invalid_account_identity')
            except AccountError as exc:
                if str(exc) in ('account_authorization_required', 'invalid_account_identity'):
                    await asyncio.to_thread(self.persistence.invalidate, opaque)
                raise
            return evidence

    async def logout(self, opaque):
        async with self.lock(opaque):
            try:
                _, tokens = await asyncio.to_thread(self.persistence.read, opaque)
            except AccountError:
                tokens = None
            await asyncio.to_thread(self.persistence.remove, opaque)
            if tokens:
                try:
                    await self.client.revoke(tokens)
                except AccountError:
                    # Local session is gone even during an issuer outage.
                    return False
            return True
