import asyncio
import json
import os

from cryptography.fernet import Fernet
import pytest

from server.runtime import RuntimeError, configuration, load, private_bytes


def protected(path,data):
    path.write_bytes(data if isinstance(data,bytes) else data.encode())
    path.chmod(0o600)
    return str(path)


@pytest.fixture
def configured(tmp_path):
    tmp_path.chmod(0o700)
    data=dict(enabled=True,coin_enabled=False,issuer='https://accounts.example.test',
        client_id='lazyingart-platform-web',audience='lazyingart-platform-api',
        redirect_uri='https://platform.lazying.art/api/account/callback',
        client_secret_file=protected(tmp_path/'client','c'*48),
        encryption_key_file=protected(tmp_path/'encryption',Fernet.generate_key()),
        cookie_secret_file=protected(tmp_path/'cookie','k'*48))
    path=tmp_path/'config.json'
    protected(path,json.dumps(data))
    return path,tmp_path,data


def test_disabled_needs_no_credentials_or_database(tmp_path):
    path=protected(tmp_path/'off.json','{"enabled":false}')
    app,clients=load(path,tmp_path/'absent')
    assert app and clients==[] and not (tmp_path/'absent').exists()


def test_private_read_rejects_permissions_symlinks_and_hardlinks(tmp_path):
    path=tmp_path/'secret'
    protected(path,'x')
    path.chmod(0o644)
    with pytest.raises(RuntimeError):
        private_bytes(str(path))
    path.chmod(0o600)
    link=tmp_path/'link';link.symlink_to(path)
    with pytest.raises(RuntimeError):
        private_bytes(str(link))
    os.link(path,tmp_path/'hard')
    with pytest.raises(RuntimeError):
        private_bytes(str(path))


@pytest.mark.parametrize('value',['[]','{"enabled":1}','{"enabled":false,"issuer":"guessed"}',
    '{"enabled":false,"enabled":true}','{"enabled":true}','not json'])
def test_configuration_fails_closed(tmp_path,value):
    path=protected(tmp_path/'config',value)
    with pytest.raises(RuntimeError):
        configuration(path)


@pytest.mark.parametrize('changes',[
    {'audience':'lazyartcoin-read-api'},{'client_id':'another-app'},
    {'redirect_uri':'https://other.example/callback'},{'issuer':'http://insecure.example'},
    {'coin_enabled':'true'}, {'secret':'not-a-path'},
])
def test_wrong_client_or_secret_shape_rejected(configured,changes):
    path,state,data=configured
    protected(path,json.dumps(data|changes))
    with pytest.raises(RuntimeError):
        configuration(str(path))


def test_schema_is_explicit_and_loaded_runtime_closes(configured):
    async def scenario():
        path,state,_=configured
        with pytest.raises(RuntimeError,match='schema_installation_required'):
            load(str(path),str(state))
        assert not (state/'accounts.sqlite3').exists()
        for install in (True,False):
            app,clients=load(str(path),str(state),install_schema=install)
            assert len(clients)==1 and app
            for client in clients:
                client.close()
        assert (state/'accounts.sqlite3').stat().st_mode & 0o077 == 0
    asyncio.run(scenario())


def test_reused_keys_rejected(configured):
    path,state,data=configured
    data['cookie_secret_file']=data['client_secret_file']
    protected(path,json.dumps(data))
    with pytest.raises(RuntimeError,match='independent_secrets_required'):
        load(str(path),str(state),install_schema=True)
