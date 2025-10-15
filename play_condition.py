import asyncio

condition = asyncio.Condition()


async def waiter(name):
    async with condition:
        print(f"{name} ждёт...")
        await condition.wait()
        print(f"{name} проснулся!")


async def notifier():
    await asyncio.sleep(1)
    async with condition:
        print("notifier вызывает notify(1)")
        condition.notify(1)


async def main():
    await asyncio.gather(waiter("A"), waiter("B"), waiter("C"), notifier())


asyncio.run(main())
