import bottle
from cardwiki import views
from bottle import run


if __name__ == "__main__":
    run(host='localhost', port=8080)

app = bottle.default_app()