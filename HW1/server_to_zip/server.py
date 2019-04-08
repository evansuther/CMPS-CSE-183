from bottle import get, route, run, template, view, static_file

@get('/')
def index():
    return template('news_template', dict())

# Let's add some code to serve jpg images from our static images directory.
# A request looks like /images/chi0.jpg
# route takes param via regex, must be filename.jpg
@route('/images/<filename:re:.*\.jpg>')
def serve_image(filename):
    return static_file(filename, root='images', mimetype='image/jpg')

@route('/images/<filename:re:.*\.png>')
def serve_image(filename):
    return static_file(filename, root='images', mimetype='image/png')

# Code for serving css stylesheets from /css directory.
@route('/css/<filename:re:.*\.css>')
def serve_css(filename):
    return static_file(filename, root='css', mimetype='text/css')

run(reloader=True, host='localhost', port=8080, debug=True)

