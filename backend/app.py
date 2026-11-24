"""
Know Thyself AI - Flask Application Factory
Team CORE FOUR — wHACKiest 2026
Initializes application, blueprints, static assets, and template rendering.
"""

from pathlib import Path
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from backend.config import Config

from backend.routes.health_routes import health_bp
from backend.routes.auth_routes import auth_bp
from backend.routes.user_routes import user_bp
from backend.routes.wellness_routes import wellness_bp
from backend.routes.analytics_routes import analytics_bp
from backend.routes.ai_routes import ai_bp
from backend.routes.upload_routes import upload_bp
from backend.routes.habit_routes import habit_bp
from backend.routes.report_routes import report_bp


def create_app(config_class=Config) -> Flask:
    """Creates and configures the Flask application."""
    base_dir = Path(__file__).resolve().parent.parent
    frontend_dir = base_dir / "frontend"
    static_folder = frontend_dir / "static"
    template_folder = frontend_dir / "templates"

    app = Flask(
        __name__,
        static_folder=str(static_folder),
        template_folder=str(template_folder)
    )
    app.config.from_object(config_class)

    # Enable Cross-Origin Resource Sharing
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register API Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(wellness_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(habit_bp)
    app.register_blueprint(report_bp)

    @app.route("/")
    def index():
        """Serves the single-page application dashboard and landing page."""
        return render_template("index.html")

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("index.html"), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
