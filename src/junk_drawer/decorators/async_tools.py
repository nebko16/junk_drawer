"""
@await_me - A decorator that makes traditional synchronous functions awaitable
==============================================================================

Runs the passed synchronous function in a thread, and returns a `asyncio.Future`
object, which is an awaitable coroutine that can be run along with other
asynchronous functions to prevent it from blocking the event loop for your
otherwise asynchronous code. This allows the synchronous function to be used
with `await`, `asyncio.create_task()`, `asyncio.gather()`, etc. for concurrent
execution within an asyncio event loop. You can even use this decorator for
instance methods, class methods, and even static methods.

Standard procedural functions or instance methods, use: `@await_me`
Class methods: `@classmethod_await_me`  Use this in place of @classmethod.
Static methods: `@staticmethod_await_me`  Use this in place of @staticmethod.

The class method and static method decorators might cause your LSP to mark
your methods as incorrect syntax, but that's just a limitation of the LSP.

!!! Do NOT add the `async` keyword to your existing function definition !!!

You simply add the decorator `@await_me`, and that's it.  It's now awaitable.
The decorator wraps your existing function with an async wrapper, which takes
care of this automatically, so adding the decorator is literally all that you
need to do to be able to treat your function as an awaitable async function.

 Synchronous: def blocker(): time.sleep(1)
Asynchronous: @await_me
              def blocker(): time.sleep(1)

If you need something like this for a version of python before version 3.9, you
can replace `asyncio.to_thread` with `concurrent.futures.ThreadPoolExecutor`. It
requires a bit more than that, but basically you create an executor object, then
you get the running loop with asyncio.get_running_loop(), then call the returned
loop object's run_in_executor() method to run the decorated function with the
executor in a separate thread , and you'll need to await this line. But honestly
it's better to just migrate to python 3.9+ if you're able to.

Note:
    The decorated function should be used in an async context, and awaited,
    to ensure proper asynchronous execution. It can be easy to incorrectly
    assume that you can use the below example syntax to run two functions
    asynchronously:

    (sequential execution) Runs blocker_1, then after completion, blocker_2 runs
    -----------------------------------------------------------------------------
    await blocker_1()
    await blocker_2()

    (concurrent execution) Runs both blocker_1 and blocker_2 concurrently
    -----------------------------------------------------------------------------
    async def parent():
        await asyncio.gather(blocker_1(), blocker_2())
    asyncio.run(parent())

Args:
     blocker_func (Callable): A synchronous function that you want to make
                              compatible with asyncio.

Returns:
        Callable: An awaitable coroutine that can be run asynchronously.

Usage example:
    -----------------------------------------------------------------------------
    from junk_drawer.decorators import await_me

    @await_me
    def io_blocker(s):
        time.sleep(s)

    async awaitable(s):
        await asyncio.sleep(s)

    async main():
        await asyncio.gather(io_blocker(5), awaitable(5))

    if __name__ == '__main__':
        asyncio.run(main())
        # completes in 5 seconds
    -----------------------------------------------------------------------------
"""
import asyncio
from functools import wraps
from typing import Callable, Any, Coroutine, TypeVar, Type


# Typing notes:
#   Callable[..., ReturnType] represents a callable object that returns ReturnType
#   Coroutine[Any, Any, ReturnType] represents a coroutine that returns ReturnType
ReturnType = TypeVar('ReturnType')

#   Type variable used to indicate the class itself
T = TypeVar('T')


def await_me(blocker_func: Callable[..., ReturnType]) -> Callable[..., Coroutine[Any, Any, ReturnType]]:
    """
    decorator to make a synchronous function awaitable (and therefore, async-compatible)

    Do NOT add `async` keyword to your existing synchronous function.  You only need to add this decorator.
    """
    @wraps(blocker_func)
    async def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        if asyncio.iscoroutinefunction(blocker_func):
            return await blocker_func(*args, **kwargs)  # type: ignore
        return await asyncio.to_thread(blocker_func, *args, **kwargs)  # type: ignore
    return wrapper


def staticmethod_await_me(blocker_func: Callable[..., ReturnType]) -> Callable[..., Coroutine[Any, Any, ReturnType]]:
    """
    decorator to make a synchronous staticmethod awaitable (and therefore, async-compatible)

    Do NOT add `async` keyword to your existing synchronous function.  You only need to add this decorator.

    Specifically for this decorator, you replace the existing @staticmethod decorator with this one.
    """
    @wraps(blocker_func)
    async def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
        if asyncio.iscoroutinefunction(blocker_func):
            return await blocker_func(*args, **kwargs)  # type: ignore
        return await asyncio.to_thread(blocker_func, *args, **kwargs)  # type: ignore
    return staticmethod(wrapper)


def classmethod_await_me(blocker_func: Callable[..., ReturnType]) -> Callable[[Type[T], Any], Coroutine[Any, Any, ReturnType]]:
    """
    decorator to make a synchronous classmethod awaitable (and therefore, async-compatible)

    Do NOT add `async` keyword to your existing synchronous function.  You only need to add this decorator.

    Specifically for this decorator, you replace the existing @classmethod decorator with this one.
    """
    @wraps(blocker_func)
    async def wrapper(cls: Type[T], *args: Any, **kwargs: Any) -> ReturnType:
        if asyncio.iscoroutinefunction(blocker_func):
            return await blocker_func(*args, **kwargs)  # type: ignore
        return await asyncio.to_thread(blocker_func, cls, *args, **kwargs)  # type: ignore
    return classmethod(wrapper)
