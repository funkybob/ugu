-----------------------
Stability & Reliability
-----------------------

So far, things are looking good. But remember the old saying about putting all
your eggs in one basket?

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
