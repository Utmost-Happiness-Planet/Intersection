import asyncio
import json
import queue
import time

import websockets
from mcdreforged.api.all import *

url = 'ws://localhost:8080/MCDR'
headers = {'server_name': 'MCDR'}
start_time = time.time()
mcdr_pool = []
q = queue.Queue(100)


async def qq2mcdr(ws, log):
    global mcdr_pool
    async for msg in ws:
        msg = json.loads(msg)
        if 'action' in msg:
            log(f'调用API {msg["action"]} 参数 {msg["params"]}')
        else:
            raise Exception('数据类型错误!')


async def heartbeat(ws, log):
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
            else:
                await asyncio.sleep(2)
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
                task_list = [qq2mcdr(ws, log), heartbeat(ws, log), mcdr2qq(ws, log)]
                for task in [asyncio.create_task(task) for task in task_list]:
                    await task
        except Exception as e:
            log(f'{e}\n连接已断开, 十秒后重连...')
            await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(main())