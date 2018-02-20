---------------
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

If we now look at our process list, you may notice quicky that we can't tell
which one is our HTTP worker, and which is our App! One again, uWSGI provides,
with a series of options to control the process name (or `procname`)::

    --procname-prefix                      add a prefix to the process names
    --procname-prefix-spaced               add a spaced prefix to the process names
    --procname-append                      append a string to process names
    --procname                             set process names
    --procname-master                      set master process name
    --emperor-procname                     set the Emperor process name

To make our lives easier, we can use another `Magic Variable` to set the name
for us: %c - the name of the directory containing the config file.

.. code-block:: ini
   :caption: http.ini
   :linenos:
   :emphasize-lines: 6

   [uwsgi]
   strict = true
   master = true
   chdir = %d

   procname-prefix = %c
   http = :8000
   http-keepalive = 1
   http-auto-gzip = true
   http-to = 127.0.0.1:8001

   processes = 0

   req-logger = file:logs/request.log
   logger = file:logs/uwsgi.log
