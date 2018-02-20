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
   http-keepalive = 1
   http-auto-gzip = true
   http-to = 127.0.0.1:8001

   processes = 0

   req-logger = file:logs/request.log
   logger = file:logs/uwsgi.log

First we use the ``chdir`` option sets the current working directory. uWSGI
translates ``%d`` to the directory of the config file. There are a number of
other `Magic Variable` that uWSGI undestands, as documented `here
<http://uwsgi-docs.readthedocs.io/en/latest/Configuration.html#magic-variables>`_.

Next we add the ``req-logger`` option to log requests to one file, and
``logger`` to log other messages to another.
