import logging
import json
from aiohttp import web

async def index(request):
    return web.FileResponse(path="public/index.html", headers={'Content-Type': 'text/html'})

async def favicon(request):
    return web.Response(text=None)

async def websocket_handler(request):
    ws = web.WebSocketResponse(heartbeat=5.0)
    await ws.prepare(request)
    websockets.add(ws)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                websockets.remove(ws)
                await ws.close()
            else:
                await ws.send_str(msg.data + "/answer")
        elif msg.type == aiohttp.WSMsgType.ERROR:
            websockets.remove(ws)
            logger.error("ws connection closed with exception %s" % ws.exception())
    logger.info('ws connection closed')

    return ws

async def schedule_update(payload):
    closing = [ws for ws in websockets if ws.closed]
    for ws in closing:
        websockets.remove(ws)
    for ws in websockets:
        await ws.send_str(json.dumps(payload))

async def run_web_app(image_path):
    app = web.Application()
    app.add_routes([
        web.get('/', index),
        web.get('/favicon.ico', favicon),
        web.get('/ws', websocket_handler),
        web.static('/images', image_path),
        web.static('/', 'public')
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner)
    await site.start()

websockets = set()
logger = logging.getLogger()
