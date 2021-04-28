import asyncio
loop = asyncio.get_event_loop()

#@asyncio.coroutine
#def hello():
#    print('Hello')
#    yield from asyncio.sleep(3)
#    print('World!')

async def hello():
    print('Hello')
    await asyncio.sleep(3)
    print('World!')

if __name__ == '__main__':
    for i in range(10):
        asyncio.ensure_future(hello())
    loop.run_forever()
