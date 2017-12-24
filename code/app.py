
def application(env, start_response):
   start_response('200 OK', [('Content-Type', 'text/html')])
   yield b'''
<!DOCTYPE html>
<html>
  <head>
    <title> Welcome! </title>
  </head>
  <body>
    <p> Welcome! </p>
  </body>
</html>'''


