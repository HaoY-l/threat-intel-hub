from flask import Blueprint, request, jsonify
from data.db_init import get_db_connection
import logging

# 创建蓝图
cve_bp = Blueprint('cve', __name__, url_prefix='/')


@cve_bp.route('/cve', methods=['GET'])
def query_cve():
    # 获取查询参数
    cve_id = request.args.get('cve_id')
    try:
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        if cve_id:
            # 查询单个 CVE
            query = "SELECT * FROM cve_data"
            cursor.execute(query, (cve_id,))
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            if result:
                return jsonify(result)
            else:
                return jsonify({"message": f"No CVE found for ID: {cve_id}"}), 404
        else:
            # 查询所有 CVE 数据
            query = "SELECT * FROM cve_data ORDER BY published DESC LIMIT 500"
            cursor.execute(query)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            return jsonify(results)

    except Exception as err:
        logging.exception("CVE 查询接口出错")
        return jsonify({"error": str(err)}), 500
