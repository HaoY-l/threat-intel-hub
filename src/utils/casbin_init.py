# src/utils/casbin_init.py
import os
import casbin
from casbin.persist.adapters import FileAdapter

# 全局 enforcer（供其他模块直接使用）
enforcer = None

def init_casbin():
    """初始化 Casbin（不依赖 Flask，不需要 app）"""

    global enforcer

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    model_path = os.path.join(base_dir, "model.conf")
    policy_path = os.path.join(base_dir, "policy.csv")

    adapter = FileAdapter(policy_path)

    # 生成 enforcer
    enforcer = casbin.Enforcer(model_path, adapter)

    return enforcer
