----------
Web server
----------

Now we need something to serve the static assets of our project - the CSS, JS,
images, and so on.

Fortunately, uWSGI provides a built in helper for this: ``--check-static``.

We just need to specify where to look for the static assets, and uWSGI will
check every request to see if a file exists.

Let's create a ``static/`` directory in our project, and start a CSS file in there:

.. code-block:: css
   :caption: static/base.css

   html { box-sizing: border-box }
   *, *:before, *:after { box-sizing: inherit; }

And we can ask uWSGI to check there like this:

.. code-block:: bash

   (venv)$ uwsgi --master --http-socket :8000 --pythonpath code/ --module app --check-static static/

Now let's see if it gets served. Visit http://127.0.0.1:8000/base.css

However, this means one of our workers is busy handling this, instead of
processing our app. Once again, uWSGI has a solution: offload threads.

We can ask uWSGI to start one or more threads per worker task to handle
"offload" work. The easiest of which is serving static content. This is done
using an event driven, asynchronous system that allows for a lot of
concurrency, and in a way that doesn't block our app workers.

.. code-block:: bash

   (venv)$ uwsgi --master --http-socket :8000 --pythonpath code/ --module app --check-static static/ --offload-threads 1

Now at the end of our statup, we'll see:

.. code-block:: none

   spawned 1 offload threads for uWSGI worker 1

and a request for our CSS file will yield:

.. code-block:: none

   [pid: 23783|app: -1|req: -1/3] 127.0.0.1 () {38 vars in 773 bytes} [Sun Dec 24 21:35:11 2017] GET /base.css => generated 79 bytes in 0 msecs via offload() (HTTP/1.1 200) 3 headers in 109 bytes (0 switches on core 0)

You'll notice in the log lines it says "via offload()" to let us know it
worked.