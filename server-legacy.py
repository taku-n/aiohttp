#!/bin/env python

import ssl

from aiohttp import web

FULL_CHAIN = '/etc/letsencrypt/live/hoge.com/fullchain.pem'
PRIV_KEY = '/etc/letsencrypt/live/hoge.com/privkey.pem'

async def handle(req):
    name = req.match_info.get('name', 'Anonymouns')
    text = 'Hello, ' + name + '\n'

    return web.Response(text=text)

app = web.Application()
app.add_routes([web.get('/', handle), web.get('/{name}', handle)])

tls = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
tls.load_cert_chain(FULL_CHAIN, PRIV_KEY)

web.run_app(app, host='0.0.0.0', port=8888, ssl_context=tls)
