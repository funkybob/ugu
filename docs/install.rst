-------
Install
-------

Now we'll install uWSGI. To get all the features we want, we'll need to ensure
we have the development headers for a number of packages already installed. On
Debian-like platforms this is done as follows:

.. code-block:: bash

   $ sudo apt-get install libpcre3-dev zlib1g-dev python3-dev

And now we can use ``pip`` to install uWSGI itself:

.. code-block:: bash

   (venv)$ pip install uwsgi
   $ echo uwsgi >> requirements.txt
