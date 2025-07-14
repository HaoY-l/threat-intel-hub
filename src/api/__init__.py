from flask import Blueprint
from .query import query_bp
from .query_cve import cve_bp

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 注册所有子蓝图
api_bp.register_blueprint(query_bp)
api_bp.register_blueprint(cve_bp)