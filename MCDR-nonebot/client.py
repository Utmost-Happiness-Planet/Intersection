import asyncio
import json
import time

import websockets

url = "ws://localhost:8080/MCDR"
headers = {'server_name': 'MCDR'}
start_time = time.time()
heartbeat_signal = True
mcdr_pool = []


async def qq2mcdr(ws):
    global heartbeat_signal
    global mcdr_pool
    async for msg in ws:
        msg = json.loads(msg)
        if msg["type"] == "heartbeat":
            heartbeat_signal = True
            mcdr_pool.append({
                'type': 'player',
                'name': 'MC_cubes',
                'message': '你好',
            })
        elif msg["type"] == "data":
            print(msg['value'])
        else:
            raise Exception("数据类型错误!")


async def heartbeat(ws):
    global heartbeat_signal
    while True:
        if heartbeat_signal == True:
            await ws.send(json.dumps({'type': 'heartbeat'}))
            print("pong")
            heartbeat_signal = False
        await asyncio.sleep(5)


async def mcdr2qq(ws):
    global mcdr_pool
    while True:
        if len(mcdr_pool):
            data = mcdr_pool.pop(0)
            await ws.send(json.dumps(data))
        else:
            await asyncio.sleep(2)


async def main():
    while True:
        try:
            print("初始化连接...")
            async with websockets.connect(url, extra_headers=headers) as ws:
                task_list = [qq2mcdr(ws), heartbeat(ws), mcdr2qq(ws)]
                for task in [asyncio.create_task(task) for task in task_list]:
                    await task
        except Exception as e:
            print(e, "\n连接断开!")


asyncio.get_event_loop().run_until_complete(main())
