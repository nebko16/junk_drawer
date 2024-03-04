## junk_drawer

Random things that probably don't justify an entire repo.

<hr>

### junk_drawer/decorators/async_tools

- `@await_me`
  - decorator to turn a synchronous python function into an asynchronous one.
  - this one is for normal procedural functions and also instance methods.
  - no need to add `async` keyword.  just add the `@await_me` decorator.
- `@staticmethod_await_me`
  - same as `@await_me`, but for static methods.  
  - replace the existing `@staticmethod` decorator with `@staticmethod_await_me`.
- `@classmethod_await_me`
  - same as `@await_me`, but for class methods.
  - replace the existing `@classmethod` decorator with `@classmethod_await_me`.

### Usage Example
#### Example of a synchronous function blocking your async functions
```python
import time
import asyncio

def blocker(s):
    time.sleep(s)
  
async def non_blocker(s):
    await asyncio.sleep(s)

async def main():
    blocker(3)
    await asyncio.gather(non_blocker(3))
    
if __name__ == '__main__':
    asyncio.run(main())
```
The above example runs for six seconds total, because the function `blocker()` is not 
asynchronous, so it blocks the execution of anything else.  So basically, it runs
for three seconds, and once complete, the async function is called, which also
completes after three seconds, bringing the total run time to around six seconds.

#### Same example, but using the `@await_me` decorator
```python
import time
import asyncio
from junk_drawer.decorators import await_me

@await_me
def blocker(s):
    time.sleep(s)
  
async def non_blocker(s):
    await asyncio.sleep(s)

async def main():
    await asyncio.gather(blocker(3), non_blocker(3))
    
if __name__ == '__main__':
    asyncio.run(main())
```
The above example simply adds the `@await_me` decorator to the `blocker()` function.
That allows us to treat it as we would any other asynchronous function.  We add it 
to the function list in the `asyncio.gather()` command, and both run concurrently,
bringing the total runtime down to three seconds.

This shouldn't be a permanent solution to creating everything to be asynchronous from
the start, but it's an easy way to get things migrated over to an asynchronous world
while you wait for more support in commonly used modules.