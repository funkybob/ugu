uWSGI from the ground up
========================
-----
Intro
-----

In this tutorial we're going to progressively construct a configuration for
uWSGI to serve our web app reliably and efficiently. uWSGI describes itself
thus:

    The uWSGI project aims at developing a full stack for building hosting
    services.

Modern web apps tend to be composed of several parts:

- a Web server, to handle static content
- an App server, to do the "work"
- a Cache for helping performance
- a Task Queue for jobs that the user doesn't need to wait for.

uWSGI can provide all of this, and a lot more!

Let's get started!

.. toctree::
   :maxdepth: 2

   prep
   venv
   our_app
   install
   app_server
   web_server
   config
   scaling
   compress
   stability
   emperor
   logging
   https
   security
   tasks
   caching
   jobq
   daemon
   thanks
