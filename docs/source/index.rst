.. asks documentation master file, created by sphinx on Thu Mar 16 00:10:45 2017.


``asks``
========

Contents:
_________

.. toctree::
   :maxdepth: 2

   overview-of-funcs-and-args
   a-look-at-sessions
   the-response-object
   idioms

What is asks?
_____________

``asks`` is an async HTTP lib that can best be described as an effort to bring the same level of usable abstraction that ``requests`` offers synchronous Python, to asynchronous Python programming. Ideal for API interactions, webscraping etc.

``asks`` is compatible with ``asyncio`` and ``trio``.

It is important to note that the code examples in this documentation are to showcase ``asks``, and not ``asyncio`` or ``trio``.
In real code, it would be beneficial to use things like taskgroups/nurserys and other neat tools to manage your requests.
Here's a link to ``trio``'s docs for reference:

http://trio.rtfd.io


Installation:
_____________

`asks` requires `Python 3.6.2 <https://www.python.org>`_ or newer.

The easiest way to install ``asks`` is to pip it::

    pip install asks

Internally ``asks`` uses the excellent `h11 <https://github.com/njsmith/h11>`_. It will be installed automatically.

``asks`` was built for use with `anyio <https://github.com/agronholm/anyio>`_ and `trio <https://github.com/python-trio/trio>`_

Importing ``asks``
__________________

The following code will run the ``example`` coroutine once with ``anyio`` and once with ``trio``: ::

    import asks
    import anyio
    import trio

    async def example():
        r = await asks.get('https://example.org')

    anyio.run(example)

    trio.run(example)


A quick note on the examples in these docs
__________________________________________

``asks`` began by only supporting ``curio``. It has since been ported to use ``anyio``, thus it works with ``asyncio`` as well as ``trio`` backends. The code examples use ``anyio`` throughout.
``curio`` support was dropped from ``anyio`` because supporting it required too many API incompatibilities with ``asyncio`` and ``trio``.
At any point in the examples you could switch say, ``async with anyio.TaskGroup`` to ``async with trio.open_nursery`` or ``async with asyncio.TaskGroup``, and everything would be the same bar ``anyio``/``asyncio``/``trio``'s API differences.
Internally, ``asks`` has no bias for either library.

A little example:
_________________

Here's how to grab a single request and print its content::

    # single_get.py
    import asks
    import anyio

    async def grabber(url):
        r = await asks.get(url)
        print(r.content)

    anyio.run(grabber, 'https://example.com')

    # Results in:
    # b'<!doctype html>\n<html>\n<head>\n    <title>Example Domain</title>\n\n

Making one request in an async program is a little weird, but not without its uses.
This sort of basic ``asks.get()`` would slot in quite nicely in a greater program that makes some calls here and there.


A bigger little example:
________________________

Here's an example of making 1000 calls to an API and storing the results in a list.
We'll use the ``Session`` class here to take advantage of connection pooling.::

    # many_get.py
    # make a whole pile of api calls and store
    # their response objects in a list.
    # Using the homogeneous-session.

    import asks
    import anyio

    path_list = ['a', 'list', 'of', '1000', 'paths']

    retrieved_responses = []

    s = asks.Session('https://some-web-service.com',
                      connections=20)

    async def grabber(a_path):
        r = await s.get(path=a_path)
        retrieved_responses.append(r)

    async def main(path_list):
        async with anyio.create_task_group() as tg:
            for path in path_list:
                tg.start_soon(grabber, path)

    anyio.run(main, path_list))

Now we're talkin'.

A thousand ``requests`` running async at the drop of a hat, using clean burning connection pooling to play nicely with the target server.


Why asks?
_________

If you like async, but don't like the spaghetti-docs future-laden many-looped ``asyncio`` lib, you'll probably love ``anyio`` and ``trio``. If you wish you could marry them with requests, you'll probably love ``asks``.

Nice libs like ``aiohttp`` suffer the side effect of ugliness due to being specifically for ``asyncio``.
Inspired by ``requests`` and the fancy new-age async libs, I wanted to take that lovely ultra abstraction and apply it to an async HTTP lib to alleviate some of the pain in dealing with async HTTP.


Features
________

``asks`` packs most if not all of the features ``requests`` does. The usual ``.json()``-ing of responses and such.
You can take a more in-depth look `here <https://asks.readthedocs.io/en/latest/overview-of-funcs-and-args.html>`_.

Because ``asks`` is aimed at crunching large piles of requests, its ``Session`` has some features you may not be aware of.
Sessions in ``asks`` are the main focus. More detail can be found `here <https://asks.readthedocs.io/en/latest/a-look-at-sessions.html>`_

The Future
__________
Now that ``trio`` support has been implemented, it's housecleaning time. ``asks`` has some cobwebs that need clearing, and refactoring those in to a nice silk dress is the current focus.

Contributing
____________

Contributions are very welcome :)

About
_____

``asks`` was created by Mark Jameson

https://theelous3.net

Shoutout to the fine folks of `8banana <https://github.com/8Banana>`_ and co.
