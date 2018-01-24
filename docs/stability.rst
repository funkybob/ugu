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

Scaling Further!
----------------

What about when we become "The Next Big Thing(tm)!" and need massive
scalability and redundancy? Currently to raise our scalability, we'd have to
restart our app worker.  That's not good.

Ideally, we'd have a load-balancer in front, which could spread requests across
a number of workers. And the workers could be started and stopped as needed in
reaction to demand or maintenance.

To do this, we can use the uWSGI FastRouter's "subscription server". We tell
our HTTP worker to run this, and the workers connect to it, tell it their
address, and which domains they're capable of handling requests for.

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
   http-subscription-server = :8001

   processes = 0

When it comes to the worker, how do we avoid having to manually allocate a port
to each instance? Fortunately for us, the OS will do that for us if we specify
port ``0``.

.. code-block:: ini
   :caption: uwsgi.ini
   :linenos:
   :emphasize-lines: 5,6

   [uwsgi]
   strict = true
   master = true

   socket = 127.0.0.1:0
   subscribe-to = 127.0.0.1:8001:mysite.com

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

However, many times we have multiple names for a single site - without www, or
by IP, and so on. We _could_ add multiple ``subscribe-to`` lines, but that
would get tedious fast. Instead, we can ask the uWSGI config language to do the
work for us using the @ directive.

.. code-block:: ini
   :caption: uwsgi.ini
   :linenos:
   :emphasize-lines: 6

   [uwsgi]
   strict = true
   master = true

   socket = 127.0.0.1:0
   subscribe-to = 127.0.0.1:8001:@hostnames.txt

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

Now we can maintain a file ``hostnames.txt`` which has one hostname per line.

So now we can start more and more instances, each one adding to the pool of
workers for the HTTP worker to pass off requests to.

Can we do better? We sure can! If we consider spreading out work across
multiple servers, we can move the HTTP worker onto its own server, and have the
app workers subscribe to it remotely. However, this would require us updating
them all if the HTTP worker ever changed IP.

To our rescue comes re-subscribe : the ability for a subscription server to
pass on subscriptions to another subscription server. How does this help us?
Well, instead of running a HTTP FastRouter as we have, we can run a uWSGI
FastRouter on each worker box, and have it re-subscribe to our separate HTTP
FastRouter.

To infinity, and beyond!
------------------------

"But what about redundancy?", I hear you cry. "We still have only one HTTP
worker!" As I hinted before, it's possible to have multiple subscribe-to lines
in a single config. They don't have to be to the same subscription server.

So we can set up two HTTP FastRouters, and have our per-worker-machine uWSGI
FastRouters re-subscribe to _both_ of them.

This would require you have some other load balancing mechanism across those
two, but this can be simply handled with DNS balancing.
