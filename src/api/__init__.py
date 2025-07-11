from flask import Blueprint
from .query import query_bp

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 注册所有子蓝图
api_bp.register_blueprint(query_bp)
