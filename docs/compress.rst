------------------
Compressed content
------------------


Static Content
--------------

To speed up transmission, thus reducing load times, it's common to compress
our data. When it comes to our static assets, we can spend some extra time to
compress it heavily once, and serve it pre-compressed, instead of spending the
effort to compress it every time we serve it.

The simplest way to get uWSGI to do this is with the `static-gzip-all` option,
which will mean any time we're serving static assets, if the browser supports
it, uWSGI will check if there is the same filename with a ``.gz`` extension.
If there is, it will serve that instead, with the headers to tell the browser
it's compressed.

.. code-block:: ini
   :caption: uwsgi.ini
   :linenos:
   :emphasize-lines: 15

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

   $ find static/ \( -name "*.css" -or -name "*.js" \) -exec gzip -9fk {} +

.. note::
   As of the 2.0.16 release of uWSGI it also supports Brotli compression,
   selecting it over gzip if supported by the browser. It is enabled by the
   ``static-gzip-all`` flag, also.

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

Dynamic content
---------------

So this takes care of our static assets, but what about our dynamic content?

In this case, we can easily ask our HTTP worker do handle this for us - after
all, all our responses will go through it anyway, and having a separate
process do it frees up our app workers sooner.

First we enable `http keepalive`, then we allow `auto gzip`.

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

However, this isn't quite enough yet. uWSGI won't jsut attempt to compress all
responses. We need to add a header to compressible responses to tell the HTTP
worker we want it compressed.

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
   variable we've called `RESPONSE_CONTENT_TYPE`.
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

This all leaves the ``uWSGI-Encoding`` header in the resposne. If you want to
remove this we can add the routing line after the others:

.. code-block:: ini

   response-route-run = delheader:uWSGI-Encoding
