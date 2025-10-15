import asyncio

condition = asyncio.Condition()
window_open = False


async def worker(name):
    global window_open
    while True:
        async with condition:
            await condition.wait_for(lambda: window_open)
            print(f"{name}: успел в окно!")
        # работа внутри окна
        await asyncio.sleep(3)


async def controller():
    global window_open
    while True:
        async with condition:
            window_open = True
            print("Контроллер: открыл окно")
            # condition.notify_all()
            condition.notify()
        await asyncio.sleep(2)  # окно открыто 2 секунды

        async with condition:
            window_open = False
            print("Контроллер: закрыл окно")
        await asyncio.sleep(3)


async def main():
    await asyncio.gather(worker("A"), worker("B"), controller())


asyncio.run(main())
