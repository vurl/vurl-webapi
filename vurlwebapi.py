import os
import re
from urllib.parse import quote

import redis
from hashids import Hashids
from yhttp import Application, text, statuses, validate, statuscode


__version__ = '0.3.0'


hashids = Hashids()


redis = redis.Redis()
app = Application()
app.settings.merge('''
blacklist: []
''')


def getfreshid():
    randomint = int.from_bytes(os.urandom(6), 'big')
    return hashids.encode(randomint)


def store(url):
    while True:
        freshid = getfreshid()
        if redis.setnx(freshid, url):
            break

    return freshid


@app.when
def ready(app):
    app.blacklist = set(re.compile(i) for i in app.settings.blacklist)


def blacklist(value, container, field):
    for r in app.blacklist:
        if r.match(value):
            raise statuses.conflict()

    return value


@app.route()
@validate(fields=dict(url=dict(
    required='400 Field missing: url',
    pattern=(r'^https?://.*', '400 Invalid URL'),
    callback=blacklist,
)))
@text
@statuscode('201 Created')
def post(req):
    return store(req.form['url'])


@app.route('/(.*)')
def get(req, key):
    longurl = redis.get(key)
    if not longurl:
        raise statuses.notfound()

    scheme, path = longurl.decode().split('://')
    path = quote(path)
    raise statuses.found(f'{scheme}://{path}')



