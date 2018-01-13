----------
Virtualenv
----------

In the interest of having a reliably repeatable environment, we'll use a
virtualenv.

.. code-block:: bash

   $ python3 -m venv venv
   $ . venv/bin/activate
   (venv)$

.. note::

   From here on whenever a command line is prefixed with (venv) it is
   important that command be executed with the virtualenv `activated` as is
   done here.

As we go along we will add any packages we need to a `requirements.txt` file.
Then, if we ever need to recreate our environment, we can create a new
virtualenv, and use ``pip install -r requirements.txt`` to reinstall our
packages.
