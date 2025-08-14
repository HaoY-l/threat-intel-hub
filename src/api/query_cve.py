# ============ CVE API (cve.py) ============
from flask import Blueprint, request, jsonify
from data.db_init import get_db_connection
import logging

cve_bp = Blueprint('cve', __name__, url_prefix='/')

@cve_bp.route('/cve', methods=['GET'])
def query_cve():
    """统一格式的CVE查询接口"""
    cve_id = request.args.get('cve_id')
    limit = request.args.get('limit', 500, type=int)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if cve_id:
            # 查询单个 CVE
            query = "SELECT * FROM cve_data WHERE id = %s OR cve_id = %s"
            cursor.execute(query, (cve_id, cve_id))
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            if result:
                # 统一返回数组格式，即使是单条记录
                return jsonify([result])
            else:
                return jsonify([])  # 返回空数组而不是404
        else:
            # 查询所有 CVE 数据
            query = "SELECT * FROM cve_data ORDER BY published DESC LIMIT %s"
            cursor.execute(query, (limit,))
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            # 直接返回数组，保持与现有格式一致
            return jsonify(results)

    except Exception as err:
        logging.exception("CVE 查询接口出错")
        return jsonify([]), 500  # 错误时返回空数组