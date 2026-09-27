"""Private, explicit runtime for the account consumer. No inferred issuer/secrets.

Run schema installation deliberately before serving. Public static files stay
with Caddy; this process listens only on loopback and serves fixed account routes.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import signal
import sqlite3
import stat

from cryptography.fernet import Fernet
import tornado.httpserver

from server.account_client import AccountClient, ClientConfiguration
from server.account_sessions import AccountSessions, SessionStore
from server.coin_client import CoinSummaryClient
from server.http import application
from server.storage import Database


class RuntimeError(ValueError):
    """Safe operator code, without paths or secret values."""


def private_bytes(filename, maximum=16384):
    try:
        path = Path(filename)
        if not path.is_absolute() or path.resolve(strict=True) != path:
            raise RuntimeError('private_regular_file_required')
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        with os.fdopen(fd,'rb') as handle:
            info = os.fstat(handle.fileno())
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                    or info.st_mode & 0o077 or info.st_nlink != 1 or info.st_size > maximum):
                raise RuntimeError('private_regular_file_required')
            data = handle.read(maximum+1)
            if len(data) > maximum:
                raise RuntimeError('private_regular_file_required')
            return data
    except (OSError, TypeError):
        raise RuntimeError('private_regular_file_required') from None


def _unique(pairs):
    result = {}
    for key,value in pairs:
        if key in result:
            raise RuntimeError('invalid_configuration')
        result[key] = value
    return result


def configuration(filename):
    try:
        data = json.loads(private_bytes(filename), object_pairs_hook=_unique)
        if not isinstance(data,dict) or type(data.get('enabled')) is not bool:
            raise RuntimeError('invalid_configuration')
        if not data['enabled']:
            if set(data) != {'enabled'}:
                raise RuntimeError('disabled_configuration_must_be_minimal')
            return data
        expected = {'enabled','coin_enabled','issuer','client_id','audience','redirect_uri',
                    'client_secret_file','encryption_key_file','cookie_secret_file'}
        if (set(data) != expected or type(data['coin_enabled']) is not bool
                or data['client_id'] != 'lazyingart-platform-web'
                or data['audience'] != 'lazyingart-platform-api'
                or data['redirect_uri'] != 'https://platform.lazying.art/api/account/callback'):
            raise RuntimeError('invalid_configuration')
        ClientConfiguration(data['issuer'],data['client_id'],data['audience'],data['redirect_uri'])
        return data
    except (ValueError, UnicodeError, TypeError) as exc:
        if isinstance(exc,RuntimeError):
            raise
        raise RuntimeError('invalid_configuration') from None


def load(filename, state_dir, *, install_schema=False):
    """Returns application and owned clients; no network calls or implicit migrations."""
    data = configuration(filename)
    if not data['enabled']:
        if install_schema:
            raise RuntimeError('enabled_configuration_required_for_schema')
        return application(), []
    try:
        client_secret = private_bytes(data['client_secret_file'],4096).strip().decode('ascii')
        key = private_bytes(data['encryption_key_file'],128).strip()
        cookie_secret = private_bytes(data['cookie_secret_file'],4096).strip()
        if len(client_secret) < 32 or len(cookie_secret) < 32 or len({client_secret.encode(),key,cookie_secret}) != 3:
            raise RuntimeError('independent_secrets_required')
        Fernet(key)
        state = Path(state_dir)
        if (not state.is_absolute() or state.resolve(strict=True) != state or not state.is_dir()
                or state.stat().st_uid != os.getuid() or state.stat().st_mode & 0o077):
            raise RuntimeError('private_state_directory_required')
        database_path = state/'accounts.sqlite3'
        if not install_schema and not database_path.exists():
            raise RuntimeError('schema_installation_required')
        database = Database(database_path)
        client = AccountClient(ClientConfiguration(data['issuer'],data['client_id'],data['audience'],data['redirect_uri'],client_secret))
        clients = [client]
        try:
            persistence = SessionStore(database,key,client)
            if install_schema:
                persistence.install_schema()
            with database.db() as db:
                expected = {
                    'account_attempts':{'state_digest','browser_digest','binding','payload','expires'},
                    'platform_account_sessions':{'digest','binding','issuer','subject','payload','status','refresh_started','expires'},
                }
                for table,columns in expected.items():
                    if {r['name'] for r in db.execute(f'PRAGMA table_info({table})')} != columns:
                        raise RuntimeError('schema_installation_required')
            reader = CoinSummaryClient() if data['coin_enabled'] else None
            if reader:
                clients.append(reader)
            app = application(AccountSessions(client,persistence),cookie_secret=cookie_secret,coin_reader=reader)
            return app,clients
        except BaseException:
            for owned in clients:
                owned.close()
            raise
    except (OSError, UnicodeError, ValueError, sqlite3.DatabaseError) as exc:
        if isinstance(exc,RuntimeError):
            raise
        raise RuntimeError('invalid_runtime_configuration') from None


async def serve(args):
    app, clients = load(args.config,args.state_dir,install_schema=args.install_schema)
    server = None
    try:
        if args.install_schema:
            print('schema_ready')
            return
        if args.check:
            print('runtime_configuration_valid')
            return
        # TLS/Host policy belongs to the qualified edge. Never trust arbitrary X-* headers.
        server = tornado.httpserver.HTTPServer(app,xheaders=False,max_body_size=16384,
            max_header_size=16384,body_timeout=10,idle_connection_timeout=30)
        server.listen(args.port,address='127.0.0.1')
        stopped = asyncio.Event()
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT,signal.SIGTERM):
            loop.add_signal_handler(sig,stopped.set)
        print('account_runtime_listening_on_loopback',flush=True)
        await stopped.wait()
    finally:
        if server:
            server.stop()
            await server.close_all_connections()
        for owned in clients:
            owned.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True)
    parser.add_argument('--state-dir',required=True)
    parser.add_argument('--port',type=int,default=18936)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--install-schema',action='store_true')
    group.add_argument('--check',action='store_true')
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('unprivileged_port_required')
    os.umask(0o077)
    try:
        asyncio.run(serve(args))
    except RuntimeError as exc:
        parser.exit(2,str(exc)+'\n')


if __name__ == '__main__':
    main()
