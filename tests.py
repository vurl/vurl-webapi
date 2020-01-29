import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import string

import pytest
from bddrest import Given, status, when, response, given

import vurlwebapi
from vurlwebapi import app


@pytest.fixture
def urandommock():
    backup = os.urandom
    os.urandom = lambda c: string.ascii_letters.encode()[:c]
    yield
    os.unrandom = backup


@pytest.fixture
def redismock():

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

    backup = vurl.redis
    vurl.redis = RedisMock()
    yield vurl.redis
    vurl.redis = backup


def test_shortener(urandommock, redismock):
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


def test_redirector(redismock):
    redismock.set('foo', 'https://example.com')
    with Given(
        app,
        url='/foo'
    ):
        assert status == 302
        assert response.headers['LOCATION'] == 'https://example.com'

        when(url='/notexists')
        assert status == 404

