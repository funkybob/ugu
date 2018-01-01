-------
Our app
-------

For demonstration purposes, we'll start with a minimal WSGI app, which we'll
put in a subdirectory called ``code/``:

.. code-block:: python
   :caption: code/app.py

   def application(env, start_response):
       start_response('200 OK', [('Content-Type', 'text/html')])
       yield b'''
    <!DOCTYPE html>
    <html>
      <head>
        <title> Welcome! </title>
        <link rel="stylesheet" type="text/css" href="base.css">
      </head>
      <body>
        <p> Welcome! </p>
      </body>
    </html>'''
