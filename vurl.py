import random

import redis
from yhttp import Application, text, statuses, validate, statuscode


app = Application()
redis = redis.Redis()


def store(url):
    freshid = hex(random.randint(0x0001, 0xFFFF))[2:]
    redis.set(freshid, url)
    return freshid


@app.route('/(.*)')
def get(req, key):
    longurl = redis.get(key)
    if not longurl:
        raise statuses.notfound()

    raise statuses.found(longurl.decode())


@app.route()
@validate(fields=dict(
    url=dict(
        required='400 Field missing: url',
        pattern=(r'^http://.*', '400 Invalid URL')
    )
))
@text
@statuscode('201 Created')
def post(req):
    return store(req.form['url'])

