'''
DIFFERENT WAYS OF RUNNING ASYNCIO PATTERN IN PYTHON:

1. asyncio.gather(comma separated functions with call ()) then asyncio.func_that_called_gather
2. 
'''
import asyncio

async def hello():
    print('Hello')
    await asyncio.sleep(3)
    print('World!')


# 1. GATHER AND RUN
async def gather_routine():
    await asyncio.gather(hello(), hello(), hello())
def gather_run():
    asyncio.run(gather_routine())

# 2. ENSURE_FUTURE WITH THE EVENT LOOP
def event_loop_future(): 
    loop = asyncio.get_event_loop()
    for i in range(10):
        asyncio.ensure_future(hello())
    loop.run_forever()

# 
#@asyncio.coroutine
#def hello():
#    print('Hello')
#    yield from asyncio.sleep(3)
#    print('World!')
