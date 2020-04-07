import logging
logger = logging.getLogger('websockets')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
import asyncio
import irc.client_aio
import irc.client
import ssl
import websockets
from time import time

DNA_WS = "wss://www.dnalounge.com:8003/irc/video"
SERVER = 'irc.prison.net'
PORT=6667
NICK = 'dnabot'
CHANNEL = '#dna-bridge'
ssl_context = ssl.create_default_context()

wsc = None
ircconn = None

async def websocketclient():
    global wsc
    
    while True:
        wsc = await websockets.connect(DNA_WS, ssl = ssl_context, origin = DNA_WS, ping_interval = None)
        async for i in wsc:
            when,who,what = i.split('\t')
            when = int(when)
            if when > time() - 5:
                print(when)
                print(who)
                print(what)
            
                if ircconn is not None:
                    ircconn.privmsg(CHANNEL, f"<{who}> {what}")
        wsc = None

async def ircclient():
    reactor = irc.client_aio.AioReactor(loop = asyncio.get_event_loop())
    
    global ircconn
    ircconn = await reactor.server().connect(SERVER, PORT, NICK)
    
    def on_connect(conn, event):
        print("...connected...")
        conn.join(CHANNEL)
    
    def on_pubmsg(conn, e):
        nick,rest = e.source.split('!')
        if wsc is not None:
            asyncio.ensure_future(wsc.send(f"{int(time())}\t{nick}\t{e.arguments[0]}"))
    
    ircconn.add_global_handler("welcome", on_connect)
    ircconn.add_global_handler("pubmsg", on_pubmsg)

async def start_clients():
    asyncio.ensure_future(websocketclient())
    asyncio.ensure_future(ircclient())
    
asyncio.get_event_loop().run_until_complete(start_clients())
asyncio.get_event_loop().run_forever()
