import asyncio
import json
import time
from queue import Queue

import websockets
from mcdreforged.api.all import *

url = 'ws://localhost:8080/MCDR'
headers = {'server_name': 'MCDR'}
start_time = time.time()
mcdr_pool = []
q: Queue = Queue(100)
data: dict = {}
online: dict = {}


async def qq2mcdr(ws, server: PluginServerInterface):
    global mcdr_pool
    global data
    async for msg in ws:
        msg = json.loads(msg)
        user_id = msg['params']['user_id']
        name = data['user_id_list'].get(user_id, None)
        if name:
            if online.get(name, False):
                server.execute(
                    f'/execute as {data["user_id_list"][user_id]} run say {msg["params"]["message"]}'
                )
            else:
                server.say("{" + name + "} " + msg["params"]["message"])
        elif name is None:
            server.say(
                RText(f'§6[§cnonebot§6]§r user_id: §6§l{user_id}§r 没有注册! 请点击本条提示进行注册! (本条提示仅显示一次)').
                h('点击将此user_id绑定至您的游戏ID下').c(RAction.run_command, f'!!nonebot {user_id}'))
            data['user_id_list'][user_id] = False


async def heartbeat(ws):
    try:
        while True:
            await ws.send(json.dumps({'type': 'heartbeat'}))
            await asyncio.sleep(2)
    except:
        ...


async def mcdr2qq(ws, log):
    global q
    try:
        while True:
            if q.qsize() > 0:
                data = q.get()
                log(json.dumps(data))
                await ws.send(json.dumps(data))
            await asyncio.sleep(0.5)
    except:
        ...


async def main(server: PluginServerInterface = None):
    if server is not None:
        log = server.logger.info
    else:
        log = print
    while True:
        try:
            log('初始化连接...')
            async with websockets.connect(url, extra_headers=headers) as ws:
                task_list = [qq2mcdr(ws, server), heartbeat(ws), mcdr2qq(ws, log)]
                for task in [asyncio.create_task(task) for task in task_list]:
                    await task
        except Exception as e:
            log(f'{e}\n连接已断开, 十秒后重连...')
            await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(main())