from flask import Flask, render_template
from .asset import Asset

app = Flask(__name__)
Asset(app)

@app.route('/')
def index():
    return render_template("base.html")

if __name__ == "__main__":
    app.run()
