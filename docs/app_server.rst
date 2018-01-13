----------
App server
----------

Let's try to launch a uWSGI instance running our code. We can start with:

.. code-block:: bash

   (venv)$ uwsgi --module app

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

   (venv)$ uwsgi --master --http-socket :8000 --module app

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

At the end you can see now the master process `and` a worker were launched.

`ModuleNotFoundError`? Ah, that's because our code is in the ``code``
subdirectory. Let's add that to Python's search path:

.. code-block:: bash

   (venv)$ uwsgi --master --http-socket :8000 --pythonpath code/ --module app

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
