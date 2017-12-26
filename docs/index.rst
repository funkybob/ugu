uWSGI from the ground up
========================

Intro
-----

In this tutorial we're going to progressively construct a configuration for
uWSGI to serve our web app reliably and efficiently.

Modern web apps tend to be composed of several parts::

- a Web server, to handle static content
- an App server, to do the "work"
- a Cache for helping performance
- a Task Queue for jobs that the user doesn't need to wait for.

So let's create a directory for our work to live in. We're going to create
``/srv/www/project``. The Linux Filesystem Hierarchy Standard proscribes
distributions from using the ``/sys`` namespace, so we know our work won't be
overwritten by package updates.

Our app
-------

For demonstration purposes, we'll start with a minimal WSGI app, which we'll
put in a subdirectory called ``code/``:

.. code-block:: python
   :caption: code/app.py

   def application(env, start_response):
       start_response('200 OK', [('Content-Type', 'text/html')])
       yield b'''
    <!DOCTYPE html>
    <html>
      <head>
        <title> Welcome! </title>
        <link rel="stylesheet" type="text/css" href="base.css">
      </head>
      <body>
        <p> Welcome! </p>
      </body>
    </html>'''

Virtualenv
----------

In the interest of having a reliably repeatable environment, we'll use a
virtualenv.

.. code-block:: bash

   $ python3 -m venv venv
   $ . venv/bin/activate

As we go along we will add any packages we need to a `requirements.txt` file.
Then, if we ever need to recreate our environment, we can create a new
virtualenv, and use ``pip install -r requirements.txt`` to reinstall our
packages.

Install
-------

Now we'll install uWSGI

.. dependencies

.. code-block:: bash

   $ pip install uwsgi
   $ echo uwsgi >> requirements.txt

App server
----------

Let's try to launch a uWSGI instance running our code. We can start with:

.. code-block:: bash

   $ uwsgi --module app

And will see output like:

.. code-block:: none
   :linenos:
   :emphasize-lines: 11,17

   *** Starting uWSGI 2.0.15 (64bit) on [Sun Dec 24 21:16:32 2017] ***
   compiled with version: 7.2.0 on 29 October 2017 10:12:50
   os: Linux-4.13.0-1-amd64 #1 SMP Debian 4.13.13-1 (2017-11-16)
   nodename: flasheart
   machine: x86_64
   clock source: unix
   pcre jit disabled
   detected number of CPU cores: 4
   current working directory: /home/curtis/src/git/ugu
   detected binary path: /home/curtis/src/git/ugu/venv/bin/uwsgi
   *** WARNING: you are running uWSGI without its master process manager ***
   your processes number limit is 31060
   your memory page size is 4096 bytes
   detected max file descriptor number: 1024
   lock engine: pthread robust mutexes
   thunder lock: disabled (you can enable it with --thunder-lock)
   The -s/--socket option is missing and stdin is not a socket.

There are a couple of things to note here.

The first is the warning about running without a master process. This process
controls the worker tasks, restarting them when they stop, among other things.
This is enabled with the ``--master`` option.

Next, the last message before it bails out is about a missing socket option.
So, we need to specify a socket for uWSGI to listen to. For now we'll tell it
to talk HTTP on that socket:

.. code-block:: bash

   $ uwsgi --master --http-socket :8000 --module app

.. code-block:: none
   :linenos:
   :emphasize-lines: 12,13,14

   *** Starting uWSGI 2.0.15 (64bit) on [Sun Dec 24 21:20:33 2017] ***
   ...
   thunder lock: disabled (you can enable it with --thunder-lock)
   uwsgi socket 0 bound to TCP address :8000 fd 3
   Python version: 3.6.4rc1 (default, Dec  6 2017, 10:08:29)  [GCC 7.2.0]
   *** Python threads support is disabled. You can enable it with --enable-threads ***
   Python main interpreter initialized at 0x56094c20d800
   your server socket listen backlog is limited to 100 connections
   your mercy for graceful operations on workers is 60 seconds
   mapped 145536 bytes (142 KB) for 1 cores
   *** Operational MODE: single process ***
   ModuleNotFoundError: No module named 'app'
   unable to load app 0 (mountpoint='') (callable not found or import error)
   *** no app loaded. going in full dynamic mode ***
   *** uWSGI is running in multiple interpreter mode ***
   spawned uWSGI master process (pid: 23058)
   spawned uWSGI worker 1 (pid: 23059, cores: 1)

At the end you can see now the master process _and_ a worker were launched.

`ModuleNotFoundError`? Ah, that's because our code is in the ``code``
subdirectory. Let's add that to Python's search path:

.. code-block:: bash

   $ uwsgi --master --http-socket :8000 --pythonpath code/ --module app

And we should see output like this:

.. code-block:: none
   :linenos:
   :emphasize-lines: 4,10-11

   *** Starting uWSGI 2.0.15 (64bit) on [Sun Dec 24 21:23:54 2017] ***
   ...
   Python version: 3.6.4rc1 (default, Dec  6 2017, 10:08:29)  [GCC 7.2.0]
   *** Python threads support is disabled. You can enable it with --enable-threads ***
   Python main interpreter initialized at 0x55daf0750900
   your server socket listen backlog is limited to 100 connections
   your mercy for graceful operations on workers is 60 seconds
   mapped 145536 bytes (142 KB) for 1 cores
   *** Operational MODE: single process ***
   added code/ to pythonpath.
   WSGI app 0 (mountpoint='') ready in 0 seconds on interpreter 0x55daf0750900 pid: 23197 (default app)
   *** uWSGI is running in multiple interpreter mode ***
   spawned uWSGI master process (pid: 23197)
   spawned uWSGI worker 1 (pid: 23198, cores: 1)

Next warning is about "Python threads support is disabled". For any case where
you are running only a single thread, Python can work a little faster with this
disabled. In most cases, however, we want to enable it using the
``--enable-threads`` option, as mentioned.

Finally, it has created our WSGI app, and started a worker task to handle
requests.

If we point our browser at http://127.0.0.1:8000/ we should get our message
back, and see a message logged by uwsgi:

.. code-block:: none

   [pid: 11839|app: 0|req: 1/1] 127.0.0.1 () {38 vars in 790 bytes} [Sun Dec 24 17:40:47 2017] GET / => generated 8 bytes in 0 msecs (HTTP/1.1 200) 1 headers in 45 bytes (1 switches on core 0)

Web server
----------

Now we need something to serve the static assets of our project - the CSS, JS,
images, and so on.

Fortunately, uWSGI provides a built in helper for this: check-static.

We just need to specify where to look for the static assets, and uWSGI will
check every request to see if a file exists.

Let's create a ``static/`` directory in our project, and start a CSS file in there:

.. code-block:: css
   :caption: static/base.css

   html { box-sizing: border-box }
   *, *:before, *:after { box-sizing: inherit; }

And we can ask uWSGI to check there like this:

.. code-block:: bash

   $ uwsgi --master --http-socket :8000 --pythonpath code/ --module app --check-static static/

Now let's see if it gets served. Visit http://127.0.0.1:8000/base.css

However, this means one of our workers is busy handling this, instead of
processing our app. Once again, uWSGI has a solution: offload threads.

We can ask uWSGI to start one or more threads per worker task to handle
"offload" work. The easiest of which is serving static content. This is done
efficiently, asynchronously, and in a way that doesn't block our app workers.

.. code-block:: bash

   $ uwsgi --master --http-socket :8000 --pythonpath code/ --module app --check-static static/ --offload-threads 1

Now at the end of our statup, we'll see:

.. code-block:: none

   spawned 1 offload threads for uWSGI worker 1

   [pid: 23783|app: -1|req: -1/3] 127.0.0.1 () {38 vars in 773 bytes} [Sun Dec 24 21:35:11 2017] GET /base.css => generated 79 bytes in 0 msecs via offload() (HTTP/1.1 200) 3 headers in 109 bytes (0 switches on core 0)

You'll notice in the log lines it says "via offload()" to let us know it
worked.

Config file
-----------

By now, our command line is getting quite long and tedious. So, let's use an
INI file to manage our configuration:

.. code-block:: ini
   :caption: uwsgi.ini
   :linenos:

   [uwsgi]
   master = true

   http-socket = :8000

   pythonpath = code/
   module = app

   check-static = static/
   offload-threads = 1

I like to keep things grouped by purpose.

Now we can launch it using:

.. code-block:: bash

   $ uwsgi --ini uwsgi.ini

As a precaution we're going to add `strict = true` to the start. Normally
uWSGI allows you to define variables to use later in your config file, but this
opens the possibility of typos in option names being silently ignored. Setting
strict mode disables this feature, and prevents these mistakes.

Scaling
-------

So now we have uWSGI serving our static assets, and running our web app. Great!

This works great, but with only one worker that will quickly stop being able to
handle a busy site.

The first steps to scaling are to increase the number of processes and/or
threads running as workers.

In uWSGI this is a matter of specifying ``--processes`` and ``--threads``. Each
process will run as many threads as we specify. Additionally, we can use the
``--cheaper`` option to scale down processes when we're not busy.

.. code-block:: ini
   :caption: uwsgi.ini
   :linenos:
   :emphasize-lines: 6-8

   [uwsgi]
   strict = true
   master = true

   http-socket = :8000
   processes = 4
   cheaper = 1
   threads = 2

   pythonpath = code/
   module = app

   check-static = static/
   offload-threads = 1

.. note::
   Adding a ``threads`` setting implicitly sets ``enable-threads``.

For even greater flexibility, we can move the HTTP handling out into its own
worker. So instead of ``http-socket`` we're now going to use ``http``.

.. code-block:: ini
   :caption: uwsgi.ini
   :linenos:
   :emphasize-lines: 5

   [uwsgi]
   strict = true
   master = true

   http = :8000
   processes = 4
   cheaper = 1
   threads = 2

   pythonpath = code/
   module = app

   check-static = static/
   offload-threads = 1

Now you'll see at the end of the startup:

.. code-block:: none

   *** uWSGI is running in multiple interpreter mode ***
   spawned uWSGI master process (pid: 25196)
   spawned uWSGI worker 1 (pid: 25198, cores: 2)
   spawned 1 offload threads for uWSGI worker 1
   spawned uWSGI http 1 (pid: 25200)

Compressed content
------------------

To speed up transmission, it's common to compress our data. When it comes to
our static assets, we can spend some extra time once to compress it heavily,
and serve it pre-compressed, instead of spending the effort to compress it
every time we serve it.

The simplest way to get uWSGI to do this is with the `static-gzip-all` option,
which will mean any time we're serving static assets, if the browser supports
it uWSGI will check if there is the same filename with a ``.gz`` extension. If
there is, it will serve that instead, with the headers to tell the browser it's
compressed.

.. code-block:: ini
   :caption: uwsgi.ini
   :linenos:
   :emphasize-lines: 12

   [uwsgi]
   strict = true
   master = true

   http = :8000
   processes = 4
   cheaper = 1
   threads = 2

   pythonpath = code/
   module = app

   offload-threads = 1
   check-static = static/
   static-gzip-all = true

Now you can compress all your static assets with the following command:

.. code-block:: bash

   $ find static/ -name "*.css" -o -name "*.js" -exec gzip -9fk \+

.. note::
   As of the 2.0.16 release of uWSGI it also supports Brotli compression,
   selecting it over gzip if supported by the browser.

.. note::
   There are other tools which can provide gzip compatible files but compress
   better than gzip. These include `advdef` from the AdvanceCOMP suite, and
   `zopfli` from Google.

How much difference does it make?

For an example, let's try a copy of Bootstrap's CSS. I've grabbed the minified
CSS for Bootstrap 3.3.7. Typically web servers will set gzip to level 5 or 6 to
get good compression, without taking too long.

+-------------------+--------+
| File              | Size   |
+===================+========+
| bootstrap.min.css | 121200 |
+-------------------+--------+
| gzip -1           |  25214 |
+-------------------+--------+
| gzip -6           |  19610 |
+-------------------+--------+
| gzip -9           |  19453 |
+-------------------+--------+
| advdef -z4        |  18325 |
+-------------------+--------+
| zopfli            |  18302 |
+-------------------+--------+

As you can see, the improvement drops off quickly. But since we're compressing
it once, and serving it repeatedly, we can spend all the time we like
compressing it.

Compressing dynamic content
~~~~~~~~~~~~~~~~~~~~~~~~~~~

So this takes care of our static assets, but what about our dynamic content?

In this case, we can easily ask our HTTP worker do handle this for us. First we
enable `http keepalive`, then we allow `auto gzip`.

.. code-block:: ini
   :caption: uwsgi.ini
   :linenos:
   :emphasize-lines: 6,7

   [uwsgi]
   strict = true
   master = true

   http = :8000
   http-keepalive = true
   http-auto-gzip = true

   processes = 4
   cheaper = 1
   threads = 2

   pythonpath = code/
   module = app

   offload-threads = 1
   check-static = static/
   static-gzip-all = true

However, this isn't quite enough yet. We need to add a header to compressible
responses to tell the HTTP worker we want it compressed.

For this, we're going to use uWSGI's internal routing feature. This lets us run
some simple logic before and after requests.

.. code-block:: ini
   :caption: uwsgi.ini
   :linenos:
   :emphasize-lines: 16-18

   [uwsgi]
   strict = true
   master = true

   http = :8000
   http-keepalive = true
   http-auto-gzip = true

   processes = 4
   cheaper = 1
   threads = 2

   pythonpath = code/
   module = app

   offload-threads = 1
   check-static = static/
   static-gzip-all = true

   collect-header = Content-Type RESPONSE_CONTENT_TYPE
   response-route-if = equal:${RESPONSE_CONTENT_TYPE};application/json addheader:uWSGI-Encoding: gzip
   response-route-if = startswith:${RESPONSE_CONTENT_TYPE};text/html addheader:uWSGI-Encoding: gzip

These three lines do as follows:

1. Instruct uWSGI to copy the `Content-Type` header from the response into a
   variable called `RESPONSE_CONTENT_TYPE`.
2. Test if the new variable equals `application/json`, and if so add a new
   header.
3. Test if the new variable contains `text/html`, and if so add a new header.

The reason for the different tests is that a `text/html` content type might
include additional fields, like a `charset` declaration. JSON, on the other
hand, is always UTF-8 encoded.

Now in the startup output you'll see:

.. code-block:: none

   *** dumping internal response routing table ***
   [rule: 0] subject: ${RESPONSE_CONTENT_TYPE};application/json func: equal action: addheader:uWSGI-Encoding: gzip
   [rule: 1] subject: ${RESPONSE_CONTENT_TYPE};text/html func: startswith action: addheader:uWSGI-Encoding: gzip
   *** end of the internal response routing table ***

If you now check the response headers you'll see our new header and, for the
right content, a ``Content-Encoding: gzip`` header.

Reliability
-----------

So far, things are looking good. But remember the old saying about putting all
our eggs in one basket?

If we want our site to be more reliable, we want to split up our jobs to avoid
a `single point of failure`.

Our first and easiest step is to move the HTTP worker into its own uWSGI
instance:

.. code-block:: ini
   :caption: http.ini
   :linenos:

   [uwsgi]
   strict = true
   master = true

   http = :8000
   http-keepalive = true
   http-auto-gzip = true

And we'll need to add a socket to our app process:

.. code-block:: ini
   :caption: uwsgi.ini
   :linenos:
   :emphasize-lines: 5

   [uwsgi]
   strict = true
   master = true

   socket = 127.0.0.1:8001

   processes = 4
   cheaper = 1
   threads = 2

   pythonpath = code/
   module = app

   offload-threads = 1
   check-static = static/
   static-gzip-all = true

   collect-header = Content-Type RESPONSE_CONTENT_TYPE
   response-route-if = equal:${RESPONSE_CONTENT_TYPE};application/json addheader:uWSGI-Encoding: gzip
   response-route-if = startswith:${RESPONSE_CONTENT_TYPE};text/html addheader:uWSGI-Encoding: gzip

The final step is to tell the HTTP worker to pass requests on to our app.

.. code-block:: ini
   :caption: http.ini
   :linenos:
   :emphasize-lines: 8

   [uwsgi]
   strict = true
   master = true

   http = :8000
   http-keepalive = true
   http-auto-gzip = true
   http-to = 127.0.0.1:8001

Now when we start our HTTP worker using ``uwsgi --ini http.ini`` we'll see output like this:

.. code-block:: none
   :linenos:

   [uWSGI] getting INI configuration from http.ini
   *** Starting uWSGI 2.0.15 (64bit) on [Mon Dec 25 11:01:55 2017] ***
   ...
   *** Operational MODE: single process ***
   *** no app loaded. going in full dynamic mode ***
   *** uWSGI is running in multiple interpreter mode ***
   spawned uWSGI master process (pid: 9439)
   spawned uWSGI worker 1 (pid: 9440, cores: 1)
   spawned uWSGI http 1 (pid: 9441)

What's this? A worker is being initialised? But we're not running an app!

uWSGI is assuming we're going to run an app, and defaults to 1 worker process. So we need to set it to 0.

.. code-block:: ini
   :caption: http.ini
   :linenos:
   :emphasize-lines: 10

   [uwsgi]
   strict = true
   master = true

   http = :8000
   http-keepalive = true
   http-auto-gzip = true
   http-to = 127.0.0.1:8001

   processes = 0

Emperor
~~~~~~~

So now we need to run two uWSGI processes. This isn't such a big deal, but simpler is more reliable, too.

uWSGI provides what's called ``Emperor`` mode. This is where we tell a uWSGI instance how to find uWSGI config files, and when it finds one it will launch and manage a new uWSGI instance running with that config.

Let's try it with the simple command line:

.. code-block:: bash

   $ uwsgi --master --emperor "*.ini"

.. note::
   We need the quotes, otherwise the shell will expand \*.ini to all the ini
   files in the current directory, and uWSGI will be invoked as
   ``uwsgi --master --emperor http.ini uwsgi.ini`` which is now what we mean.

.. code-block:: none
   :linenos:
   :emphasize-lines: 20,22

   *** Starting uWSGI 2.0.15 (64bit) on [Mon Dec 25 11:50:34 2017] ***
   compiled with version: 7.2.0 on 29 October 2017 10:12:50
   os: Linux-4.13.0-1-amd64 #1 SMP Debian 4.13.13-1 (2017-11-16)
   nodename: flasheart
   machine: x86_64
   clock source: unix
   pcre jit disabled
   detected number of CPU cores: 4
   current working directory: /home/curtis/src/git/ugu
   detected binary path: /home/curtis/src/git/ugu/venv/bin/uwsgi
   your processes number limit is 31060
   your memory page size is 4096 bytes
   detected max file descriptor number: 1024
   lock engine: pthread robust mutexes
   thunder lock: disabled (you can enable it with --thunder-lock)
   Python version: 3.6.4rc1 (default, Dec  6 2017, 10:08:29)  [GCC 7.2.0]
   *** starting uWSGI Emperor ***
   *** has_emperor mode detected (fd: 5) ***
   *** has_emperor mode detected (fd: 6) ***
   [uWSGI] getting INI configuration from uwsgi.ini
   [uwsgi-static] added check for static/
   [uWSGI] getting INI configuration from http.ini
   *** Starting uWSGI 2.0.15 (64bit) on [Mon Dec 25 11:50:34 2017] ***
   compiled with version: 7.2.0 on 29 October 2017 10:12:50
   os: Linux-4.13.0-1-amd64 #1 SMP Debian 4.13.13-1 (2017-11-16)
   nodename: flasheart
   machine: x86_64
   clock source: unix
   pcre jit disabled
   detected number of CPU cores: 4
   current working directory: /home/curtis/src/git/ugu
   detected binary path: /home/curtis/src/git/ugu/venv/bin/uwsgi
   *** dumping internal response routing table ***
   *** Starting uWSGI 2.0.15 (64bit) on [Mon Dec 25 11:50:34 2017] ***
   compiled with version: 7.2.0 on 29 October 2017 10:12:50
   [rule: 0] subject: ${RESPONSE_CONTENT_TYPE};application/json func: equal action: addheader:uWSGI-Encoding: gzip
   os: Linux-4.13.0-1-amd64 #1 SMP Debian 4.13.13-1 (2017-11-16)
   nodename: flasheart
   [rule: 1] subject: ${RESPONSE_CONTENT_TYPE};text/html func: startswith action: addheader:uWSGI-Encoding: gzip
   *** end of the internal response routing table ***
   machine: x86_64
   clock source: unix
   pcre jit disabled
   detected number of CPU cores: 4
   current working directory: /home/curtis/src/git/ugu
   detected binary path: /home/curtis/src/git/ugu/venv/bin/uwsgi
   collecting header Content-Type to var RESPONSE_CONTENT_TYPE
   your processes number limit is 31060
   your memory page size is 4096 bytes
   detected max file descriptor number: 1024
   building mime-types dictionary from file /etc/mime.types...554 entry found
   lock engine: pthread robust mutexes
   thunder lock: disabled (you can enable it with --thunder-lock)
   uwsgi socket 0 bound to TCP address 127.0.0.1:8001 fd 3
   Python version: 3.6.4rc1 (default, Dec  6 2017, 10:08:29)  [GCC 7.2.0]
   your processes number limit is 31060
   your memory page size is 4096 bytes
   detected max file descriptor number: 1024
   lock engine: pthread robust mutexes
   thunder lock: disabled (you can enable it with --thunder-lock)
   uWSGI http bound on :8000 fd 3
   Python version: 3.6.4rc1 (default, Dec  6 2017, 10:08:29)  [GCC 7.2.0]
   *** Python threads support is disabled. You can enable it with --enable-threads ***
   Python main interpreter initialized at 0x55c239675990
   your mercy for graceful operations on workers is 60 seconds
   *** Operational MODE: no-workers ***
   spawned uWSGI master process (pid: 11727)
   Mon Dec 25 11:50:35 2017 - [emperor] vassal http.ini has been spawned
   *** Python threads support is disabled. You can enable it with --enable-threads ***
   Python main interpreter initialized at 0x55864820f650
   your mercy for graceful operations on workers is 60 seconds
   *** Operational MODE: no-workers ***
   spawned uWSGI master process (pid: 11725)
   spawned uWSGI http 1 (pid: 11729)
   *** Python threads support is disabled. You can enable it with --enable-threads ***
   Python main interpreter initialized at 0x558e117d9550
   your server socket listen backlog is limited to 100 connections
   your mercy for graceful operations on workers is 60 seconds
   mapped 145536 bytes (142 KB) for 1 cores
   *** Operational MODE: single process ***
   added code/ to pythonpath.
   WSGI app 0 (mountpoint='') ready in 0 seconds on interpreter 0x558e117d9550 pid: 11728 (default app)
   *** uWSGI is running in multiple interpreter mode ***
   spawned uWSGI master process (pid: 11728)
   Mon Dec 25 11:50:35 2017 - [emperor] vassal uwsgi.ini has been spawned
   spawned uWSGI worker 1 (pid: 11730, cores: 1)
   spawned 1 offload threads for uWSGI worker 1
   Mon Dec 25 11:50:35 2017 - [emperor] vassal uwsgi.ini is ready to accept requests

This is quite a mess! But if you read carefully, you'll see the Emperor has
started, and launched two `vassal` instances. Should either of the tasks fail
for any reason the Emperor will re-launch them, with controls to fail them if
they respawn too often. Also, if their config files go away for any reason, the
Emperor will stop the vassal.

Logging
-------

To help keep track of which task is writing what, let's send our logging to
files in a ``logs/`` subdirectory.

.. code-block:: ini
   :caption: http.ini
   :linenos:
   :emphasize-lines: 4,13-14

   [uwsgi]
   strict = true
   master = true
   chdir = %d

   http = :8000
   http-keepalive = true
   http-auto-gzip = true
   http-to = 127.0.0.1:8001

   processes = 0

   req-logger = file:logs/request.log
   logger = file:logs/uwsgi.log

First we use the ``chdir`` option sets the current working directory. uWSGI
translates ``%d`` to the directory of the config file.

Next we add the ``req-logger`` option to log requests to one file, and
``logger`` to log other messages to another.

Task management
---------------

Now that things are growing, it's probably time to reorganise a little.

Since we're going to be running two services, we might as well keep them (and
their logging) in separate directories. Let's move the http config into
``/srv/www/http/``, and, for consistency, call it ``uwsgi.ini``::

   /srv/www/
   +- http/
   |  +- logs/
   |  +- uwsgi.ini
   +- project/
      +- code/
      +- static/
      +- logs/
      +- venv/
      +- uwsgi.ini

Now we can configure ``--emperor`` to look for ini files as ``/srv/www/*/uwsgi.ini``.

Caching
-------

Job queues
----------

External daemons
----------------
