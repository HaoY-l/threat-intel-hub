from flask import Blueprint
from .query import query_bp
from .query_cve import cve_bp
from .query_news import news_bp
from .alicloud_waf_listwhite import waf_listwhite
from .alicloud_waf_addwhite import waf_addwhite
from .alicloud_waf_deletewhite import waf_deletewhite
from .alicloud_waf_descblackrule import waf_descrule
from .alicloud_waf_modifyblackrule import waf_modifyblackrule
from .tools_wxgzh import wxgzh_bp
from .alicloud_waf_attackauto import waf_logs_bp
from .tools_all import tools_bp
from .ai_chat import aichat_bp
from .alicloud_waf_alert import waf_alert

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 注册所有子蓝图
api_bp.register_blueprint(query_bp)
api_bp.register_blueprint(cve_bp)
api_bp.register_blueprint(news_bp)
api_bp.register_blueprint(waf_listwhite)
api_bp.register_blueprint(waf_addwhite)
api_bp.register_blueprint(waf_deletewhite)
api_bp.register_blueprint(waf_descrule)
api_bp.register_blueprint(waf_modifyblackrule)
api_bp.register_blueprint(wxgzh_bp)
api_bp.register_blueprint(waf_logs_bp)
api_bp.register_blueprint(tools_bp)
api_bp.register_blueprint(aichat_bp)
api_bp.register_blueprint(waf_alert)
