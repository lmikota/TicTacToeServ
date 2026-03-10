import os
from flask import send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint

from app import app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SWAGGER_URL = "/docs"
API_URL = "/openapi.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "TicTacToe API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/openapi.yaml")
def openapi_spec():
    return send_from_directory(BASE_DIR, "openapi.yaml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)