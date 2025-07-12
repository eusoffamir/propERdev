from flask import Blueprint, jsonify, make_response
from app.controllers import MainController

main_bp = Blueprint('main', __name__)
main_controller = MainController()

@main_bp.route('/', methods=['GET'])
def index():
    result = main_controller.index()
    return make_response(jsonify(data=result))

def register_routes(app):
    app.register_blueprint(main_bp)
