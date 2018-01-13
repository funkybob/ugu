-------
Scaling
-------

So now we have uWSGI serving our static assets, and running our web app. Great!

This works great, but with only one worker we can only handle one request at a
time, and that will quickly stop being able to handle a busy site.

The first steps to scaling are to increase the number of processes and/or
threads running as workers.

In uWSGI this is a matter of specifying ``--processes`` and ``--threads``,
respectively. Each process will run as many threads as we specify.
Additionally, we can use the ``--cheaper`` option to scale down processes when
we're not busy.

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

This will run at least 1, and up to 4, processes, each with 2 threads, allowing
for a maximum of 8 concurrent requests.

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

We can even scale the number of HTTP workers independantly, using the
``--http-processes`` option, though a single worker process should be able to
handle quite a large number of concurrent requests.
