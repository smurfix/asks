``asks`` - Useful idioms and tricks.
====================================

Sanely making many requests (with semaphores)
_____________________________________________

A (bounded) semaphore is like a sofa (sofaphore?). It can only fit so many tasks at once.
If we have a semaphore whose maximum size is ``5`` then only ``5`` tasks can sit on it.
When one task finishes, another task can sit down.
This is an extremely simple and effective way to manage the resources used by ``asks`` when making large amounts of requests.

If we wanted to request two thousand urls, we wouldn't want to spawn two thousand tasks and have them all fight for CPU time. ::


    import asks
    import anyio

    async def worker(sema, url):
        async with sema:
            r = await asks.get(url)
            print('got ', url)

    async def main(url_list):
        sema = anyio.Semaphore(max_value=2)  # Set sofa size.
        async with anyio.create_task_group() as tg:
            for url in url_list:
                tg.start_soon(worker, sema, url)

    url_list = ['http://httpbin.org/delay/5',
                'http://httpbin.org/delay/1',
                'http://httpbin.org/delay/2']

    anyio.run(main, url_list)

This method of limiting works for the single-request ``asks`` functions and for any of the sessions' methods.

The result of running this is that the first and second url (``delay/5`` and ``delay/1``) run.
``delay/1`` finishes, and allows the third url, ``delay/2`` to run.

* After one second, ``delay/1`` finishes.
* After three seconds, ``delay/2`` finishes.
* After five seconds, ``delay/5`` finishes.


Maintaining Order
_________________

Due to the nature of async, if you feed a list of urls to ``asks`` in some fashion, and store the responses in a list, there is no guarantee the responses will be in the same order as the list of urls.

A handy way of dealing with this on an example ``url_list`` is to pass the enumerated list as a dict ``dict(enumerate(url_list))`` and then create a sorted list from a response dict.
This sounds more confusing in writing than it is in code. Take a look: ::

    import asks
    import anyio

    results = {}

    url_list = ['a', 'big', 'list', 'of', 'urls']

    async def worker(key, url):
        r = await s.get(url)
        results[key] = r

    async def main(url_list):
        url_dict = dict(enumerate(url_list))
        async with anyio.create_task_group() as tg:
            for key, url in url_dict.items():
                tg.start_soon(worker, key, url)

    sorted_results = [response for _, response in sorted(results.items())]

    s = asks.Session(connections=10)
    anyio.run(main, url_list)

In the above example, ``sorted_results`` is a list of response objects in the same order as ``url_list``.

There are of course many ways to achieve this, but the above is noob friendly. Another way of handling order would be a ``heapq``, or managing it with an object stream. Here's an example of that: ::

    import asks
    import anyio

    url_list = ["https://www.httpbin.org/get" for _ in range(50)]
    results = [None] * len(url_list)

    s = asks.Session()

    async def worker(key, url, q):
        r = await s.get(url)
        await q.send((key, r.body))
        q.close()

    async def reader(q):
        async for res in q:
            print(f"done with {res[0]}")
            results[res[0]] = res[1]
        
    async def main():
        wq, rq = anyio.create_memory_object_queue(1)
        async with anyio.create_task_group() as tg:
            tg.start_soon(reader, rq)
            for key, url in enumerate(url_list):
                tg.start_soon(worker, key, url, wq.clone())
            wq.close()
            # Here we iterate the TaskGroup, getting results as they come.

        print(results)


Handling response body content (downloads etc.)
___________________________________________________________

The recommended way to handle this sort of thing is by streaming.
The following examples use a context manager on the response body to ensure the underlying connection is always handled properly: ::

    import asks
    import anyio

    async def main():
        r = await asks.get('http://httpbin.org/image/png', stream=True)
        async with (
                await anyio.open_file('our_image.png', 'ab') as out_file,
                r.body as chunks,
            ):
            async for bytechunk in chunks:
                await out_file.write(bytechunk)

    anyio.run(main)

An example of multiple downloads with streaming: ::

    import asks
    import anyio

    from functools import partial

    async def downloader(filename, url):
        r = await asks.get(url, stream=True)
        async with await anyio.open_file(filename, 'ab') as out_file:
            async with r.body as chunks:
                async for bytechunk in chunks:
                    out_file.write(bytechunk)

    async def main():
        async with anyio.create_task_group() as tg:
            for indx, url in enumerate(['http://placehold.it/1000x1000',
                                        'http://httpbin.org/image/png']):
                func = partial(downloader, str(indx) + '.png')
                tg.start_soon(func, url)

    anyio.run(main)


The ``callback`` argument lets you pass a function as a callback that will be run on each byte chunk of response body *as the request is being processed* . A simple use case for this is downloading a file.

Below you'll find an example of a single download of an image with a given filename, and multiple downloads with sequential numeric filenames.
They are very similar to the streaming examples above.

We define a callback function ``downloader`` that takes bytes and saves 'em, and pass it in. ::

    import asks
    import anyio

    async def downloader(bytechunk):
        async with await anyio.open_file('our_image.png', 'ab') as out_file:
            await out_file.write(bytechunk)

    async def main():
        r = await asks.get('http://httpbin.org/image/png', callback=downloader)

    anyio.run(main)

What about downloading a whole bunch of images, and naming them sequentially? ::

    import asks
    import anyio

    from functools import partial

    async def downloader(filename, bytechunk):
        async with await anyio.open_file(filename, 'ab') as out_file:
            await out_file.write(bytechunk)

    async def main():
        async with anyio.create_task_group() as tg:
            for indx, url in enumerate(['http://placehold.it/1000x1000',
                                    'http://httpbin.org/image/png']):
                func = partial(downloader, str(indx) + '.png')
                tg.start_soon(partial(asks.get, url, callback=func))

    anyio.run(main)


Resending an ``asks.Cookie``
____________________________

Simply reference the ``Cookie`` 's ``.name`` and ``.value`` attributes as you pass them in to the ``cookies`` argument. ::

    import asks
    import anyio

    a_cookie = previous_response_object.cookies[0]

    async def example():
        cookies_to_go = {a_cookie.name: a_cookie.value, 'another': 'cookie'}
        r = await asks.get('http://example.com', cookies=cookies_to_go)

    anyio.run(example)
