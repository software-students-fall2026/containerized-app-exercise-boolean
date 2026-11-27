"""Created this file to start all three containers"""

from flask import Flask

app = Flask(__name__)


@app.get("/")
def home():
     """Show that the web container is running."""
     return "app is running."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
