-----------
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

   (venv)$ uwsgi --ini uwsgi.ini

As a precaution we're going to add `strict = true` to the start. Normally
uWSGI allows you to define variables to use later in your config file, but as
the syntax is exactly the same as setting a config option this opens the
possibility of typos in option names being silently ignored. Setting strict
mode disables this feature, and prevents these mistakes.