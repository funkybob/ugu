------------
Preparations
------------

This tutorial assumes you have a recent version of Python 3 installed,
including the Python3 venv module (a separate package on Debian and some other
distros).

So let's create a directory for our work to live in. We're going to create
``/srv/www/project``. The Linux Filesystem Hierarchy Standard proscribes
distributions from using the ``/sys`` namespace, so we know our work won't be
overwritten by package updates.

You will need to be root to create this directory, and change its ownership to
your own user.

.. code-block:: none

   $ su
   # mkdir /srv/www/project
   # chown myuser:myuser /srv/www/project

It's become fashionable these days to use ``sudo`` instead of ``su`` to root.
