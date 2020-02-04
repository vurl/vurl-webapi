import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import string

import pytest
from bddrest import Given, status, when, response, given

import vurlwebapi


@pytest.fixture
def app():
    app = vurlwebapi.app
    app.ready()
    yield app
    app.shutdown()


@pytest.fixture
def urandommock():
    backup = os.urandom
    os.urandom = lambda c: string.ascii_letters.encode()[:c]
    yield
    os.unrandom = backup


@pytest.fixture
def redis():

    class RedisMock:
        def __init__(self):
            self.maindict = dict()

        def get(self, key):
            return self.maindict.get(key, '').encode()

        def set(self, key, value):
            self.maindict[key] = value

        def setnx(self, key: str, value):
            if not self.maindict.get(key):
                self.set(key, value)
                return 1
            return 0

        def flushdb(self):
            self.maindict.clear()

    backup = vurlwebapi.redis
    vurlwebapi.redis = RedisMock()
    yield vurlwebapi.redis
    vurlwebapi.redis = backup


def test_shortener(app, urandommock, redis):
    app.settings.merge(r'''
    blacklist:
      - ^https?://(www\.)?vurl\.ir.*
    ''')
    app.ready()

    with Given(
        app,
        verb='POST',
        json=dict(url='http://example.com/')
    ):
        assert status == 201
        assert response.text == 'LJO1vnZOE4'

        when(json=dict(url='invalidurl'))
        assert status == 400

        when(json=given - 'url')
        assert status == '400 Field missing: url'

        # Blacklist
        when(json=dict(url='http://vurl.ir'))
        assert status == 409

        when(json=dict(url='https://vurl.ir'))
        assert status == 409

        when(json=dict(url='http://www.vurl.ir'))
        assert status == 409

        when(json=dict(url='https://www.vurl.ir'))
        assert status == 409

        when(json=dict(url='https://vurl.ir/foo'))
        assert status == 409

        # Encoding
        redis.flushdb()
        when(json=dict(url='https://example.com/#/baz'))
        assert status == 201
        assert redis.get(response.text) == b'https://example.com/#/baz'

        redis.flushdb()
        when(json=dict(url='https://example.com/\u265F/baz'))
        assert status == 201
        assert redis.get(response.text) == b'https://example.com/%E2%99%9F/baz'


def test_redirector(app, redis):
    redis.set('foo', 'https://example.com')
    redis.set('bar', 'https://example.com/%E2%99%9F')
    redis.set('baz', 'https://example.com/#/baz')
    with Given(
        app,
        url='/foo'
    ):
        assert status == 302
        assert response.headers['LOCATION'] == 'https://example.com'

        when('/notexists')
        assert status == 404

        when('/bar')
        assert status == 302
        assert response.headers['LOCATION'] == 'https://example.com/%E2%99%9F'

        when('/baz')
        assert status == 302
        assert response.headers['LOCATION'] == 'https://example.com/#/baz'

