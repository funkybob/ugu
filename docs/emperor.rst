-------
Emperor
-------

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