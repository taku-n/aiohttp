#!/bin/env python

# wscat -c wss://hoge.com:8888/ws

import asyncio
import ssl
import weakref

import aiohttp
from aiohttp import web, WSCloseCode

FULL_CHAIN = '/etc/letsencrypt/live/hoge.com/fullchain.pem'
PRIV_KEY = '/etc/letsencrypt/live/hoge.com/privkey.pem'

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    try:
        loop.run_forever()
    finally:
        pass

async def start_server():
    tls = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    tls.load_cert_chain(FULL_CHAIN, PRIV_KEY)

    runner = create_runner()
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8888, ssl_context=tls)
    try:
        await site.start()
    finally:
        pass

def create_runner():
    app = web.Application()
    app.add_routes([
            web.get('/', handler_http),
            web.get('/ws', handler_websocket),
    ])
    app['websockets'] = weakref.WeakSet()
    app.on_shutdown.append(on_shutdown)

    return web.AppRunner(app)

async def on_shutdown(app):
    for ws in set(app['websockets']):
        await ws.close(code=WSCloseCode.GOING_AWAY, message='Server Shutdown')

async def handler_http(req):
    return web.Response(text='hello, world\n')

async def handler_websocket(req):
    ws = web.WebSocketResponse()
    await ws.prepare(req)

    req.app['websockets'].add(ws)
    try:
        await ws.send_str('To disconnect, type "close".')
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    await ws.send_str('You sent ' + msg.data + '.')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception: %s' % ws.exception())
    finally:
        req.app['websockets'].discard(ws)

    return ws

if __name__ == '__main__':
    main()
