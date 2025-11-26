import os
import casbin
from src.utils.casbin_adapter import DatabaseAdapter

# 全局 enforcer（供 app.py 使用）
enforcer = None

def init_casbin():
    """初始化 Casbin（使用数据库策略）"""
    global enforcer

    # 模型文件路径（仍然需要）
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    model_path = os.path.join(base_dir, "model.conf")

    adapter = DatabaseAdapter()
    enforcer = casbin.Enforcer(model_path, adapter)
    enforcer.load_policy()  # 从数据库加载策略
    return enforcer
