import asyncio

stack = asyncio.LifoQueue()


async def worker(name):
    while True:
        item = await stack.get()
        if item is None:
            print(f"{name}: завершает работу")
            break
        print(f"{name}: обработал {item}")
        await asyncio.sleep(1)
        stack.task_done()


async def producer():
    for i in range(5):
        await asyncio.sleep(0.5)
        await stack.put(i)
        print(f"Производитель: добавил {i}")
    # сигналы завершения
    for _ in range(2):
        await stack.put(None)


async def main():
    workers = [asyncio.create_task(worker(f"Рабочий-{i}")) for i in range(2)]
    await producer()
    await stack.join()
    for w in workers:
        await w


asyncio.run(main())
