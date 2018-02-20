--------
Security
--------

Security is a very big topic to cover, but there are a number of practices you
can follow to help avoid a majority of attacks and weaknesses. Two of the most
effective of these practices are known as "Minimal Attack Surface", and the
"Principle of Least Privilege".


Attack Surface
--------------

Your "attack surface" is how much of your system is visible to external
attackers. By keeping to a minimum what each service does, and can do, you
reduce the impact of that task being compromised.

This is one reason we moved our HTTP worker into its own task. If we wanted to
go even further, we could build a version of uWSGI with only the modules needed
to perform that task.

Least Privilege
---------------

Ideally, the user and group each task runs as should only have enough
permission to read and write the files it needs.

The way we do this in our uWSGI setup is with the ``--uid`` and ``--gid`` options.

In our HTTP worker, we use ``--http-uid`` and ``--http-gid``. However, this
task needs access to a privileged port - port 80 (on Unix like systems all
ports below 1024 require root to bind). Once again, uWSGI has a solution:
shared sockets.

.. code-block:: ini
   :caption: http.ini
   :linenos:
   :emphasize-lines: 5,8

   [uwsgi]
   strict = true
   master = true
   chdir = %d
   shared-socket = :80

   procname-prefix = %c
   http = =0
   http-uid = www-data
   http-gid = www-data
   http-keepalive = 1
   http-auto-gzip = true
   http-to = 127.0.0.1:8001

   processes = 0

   req-logger = file:logs/request.log
   logger = file:logs/uwsgi.log

So in line 5 we tell uWSGI to bind the port, ready to be shared with one of its
worker tasks. Then we tell the HTTP worker to use the first shared socket. So
the process launches as root, creates the socket, the HTTP worker drops down to
the `www-data` user, and grabs the local handle to use the root-created socket.
