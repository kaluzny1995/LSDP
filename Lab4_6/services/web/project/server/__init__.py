import os
from flask import Flask

from server.main.views import main_blueprint


app = Flask(
    __name__,
    template_folder='../client/templates',
    static_folder='../client/static'
)


app_settings = os.getenv(
    'APP_SETTINGS',
    'project.server.config.DevelopmentConfig'
)
app.config.from_object(app_settings)

app.register_blueprint(main_blueprint)
