"""Main Flask application for Grocery Price Finder."""

from flask import Flask, redirect, url_for

from dashboard import dashboard_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)


@app.get("/")
def home():
    """Redirect users to the grocery dashboard."""
    return redirect(url_for("dashboard.dashboard"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
