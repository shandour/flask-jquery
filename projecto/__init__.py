# -*- coding: utf-8 -*-
from flask import Flask


def create_app(settings_module='projecto.settings'):
    app = Flask(__name__)
    app.config.from_object(settings_module)
    if not app.testing:
        app.config.from_envvar('PROJECTO_SETTINGS_FILE')

    from projecto.models import db
    db.init_app(app)

    from projecto.frontend import views
    from projecto.frontend import frontend_bp, api_bp
    app.register_blueprint(frontend_bp)
    app.register_blueprint(api_bp)

    from projecto.navigation import nav
    nav.init_app(app)

    from projecto.security import security, user_datastore
    from projecto.forms import UpgradedRegisterForm
    security.init_app(app, datastore=user_datastore,
                      register_form=UpgradedRegisterForm)

    @app.context_processor
    def inject_nav():
        return {'nav': nav}

    return app
