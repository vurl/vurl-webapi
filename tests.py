import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import random
import string

import pytest
from bddrest import Given, status, when, response, given

import vurl
from vurl import app


@pytest.fixture
def randommock():
    backup = random.randint
    random.randint = lambda a, b: 0xF00
    yield
    random.randint = backup


@pytest.fixture
def redismock():

    class RedisMock:
        def __init__(self):
            self.maindict = dict()

        def get(self, key):
            return self.maindict.get(key, '').encode()

        def set(self, key, value):
            self.maindict[key] = value

    backup = vurl.redis
    vurl.redis = RedisMock()
    yield vurl.redis
    vurl.redis = backup


def test_shortener(randommock, redismock):
    with Given(
        app,
        verb='POST',
        json=dict(url='http://example.com')
    ):
        assert status == 201
        assert response.text == 'f00'

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

