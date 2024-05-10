from waitress import serve
from cherrybin import create_app

if __name__ == "__main__":
    serve(create_app(), listen="*:5000")
