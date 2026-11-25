"""Starts the backend:  python app.py   (listens on http://localhost:5001)"""
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from database import db
from routes import admin, auth, checkins, feedback, jobs, matches, notifications, profiles
from seed import seed_basics, seed_demo


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app, origins=[o.strip() for o in app.config["CORS_ORIGINS"].split(",")])
    db.init_app(app)

    for module in (auth, profiles, admin, matches, feedback, checkins, jobs, notifications):
        app.register_blueprint(module.bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not found."}), 404

    @app.errorhandler(405)
    def wrong_method(_):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def server_error(_):
        db.session.rollback()  # leave the database session clean for the next request
        return jsonify({"error": "Something went wrong on the server."}), 500

    with app.app_context():
        db.create_all()
        seed_basics()
        if app.config["LOAD_DEMO_DATA"]:
            seed_demo()
    return app


if __name__ == "__main__":
    create_app().run(port=5001, debug=True)
