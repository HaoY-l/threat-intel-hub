from datetime import datetime
import os,json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, precision_recall_curve, auc
)
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout
from keras.layers import Input
from flask import Blueprint, jsonify, request
import nltk
from nltk.tokenize import word_tokenize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from flask_cors import CORS
from data.db_init import get_db_connection
from src.routes.email.get_qx_email import main as get_qx_email

# 创建蓝图
phishing_bp = Blueprint('phishing_bp', __name__, url_prefix='/phishing')

# 基础路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PHISHING_DIR = os.path.join(BASE_DIR, 'src', 'routes', 'phishing')
DATASET_FILE = os.path.join(PHISHING_DIR, 'spam_assassin.csv')
MODEL_FILE = os.path.join(PHISHING_DIR, 'phishing_model.h5')
STATIC_DIR = os.path.join(PHISHING_DIR, 'static')
LOG_FILE = os.path.join(PHISHING_DIR, 'prediction_results.log')
LOCAL_NLTK_DIR = os.path.join(PHISHING_DIR, 'nltk_data')

# 全局变量
model = None
tfidf = None
X_train = X_test = y_train = y_test = None


def ensure_local_nltk():
    """确保 NLTK 会优先从本地目录读取资源"""
    if LOCAL_NLTK_DIR not in nltk.data.path:
        nltk.data.path.insert(0, LOCAL_NLTK_DIR)
    try:
        nltk.data.find('tokenizers/punkt')
        print("NLTK punkt 已在本地找到。")
    except LookupError:
        print("本地未找到 punkt，尝试下载到本地 nltk_data ...")
        os.makedirs(LOCAL_NLTK_DIR, exist_ok=True)
        nltk.download('punkt', download_dir=LOCAL_NLTK_DIR, quiet=False)


def load_resources():
    """加载数据集、分词、向量化、划分训练集和测试集"""
    global tfidf, X_train, X_test, y_train, y_test

    if not os.path.exists(STATIC_DIR):
        os.makedirs(STATIC_DIR)

    print("加载数据集...")
    df = pd.read_csv(DATASET_FILE)

    ensure_local_nltk()
    df['tokens'] = df['text'].apply(word_tokenize)

    print("特征向量化...")
    tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
    X = tfidf.fit_transform(df['text']).toarray()
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )


def build_model(input_dim):
    model = Sequential([
        Input(shape=(input_dim,), name='input_layer'),
        Dense(128, activation='relu'),
        Dropout(0.2),
        Dense(64, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model


def train_and_save_model():
    """训练并保存模型"""
    global model
    model = build_model(X_train.shape[1])
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=5,
        batch_size=32,
        verbose=1
    )
    model.save(MODEL_FILE)

    y_pred_proba = model.predict(X_test)
    y_pred = (y_pred_proba > 0.5).astype(int)

    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred)
    }

    hist_df = pd.DataFrame(history.history)
    hist_df.to_csv(os.path.join(STATIC_DIR, 'training_history.csv'), index=False)

    with open(os.path.join(STATIC_DIR, 'model_metrics.txt'), 'w') as f:
        for k, v in metrics.items():
            f.write(f"{k}: {v:.4f}\n")

    cm = confusion_matrix(y_test, y_pred)
    np.save(os.path.join(STATIC_DIR, 'confusion_matrix.npy'), cm)

    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    np.savez(os.path.join(STATIC_DIR, 'roc_data.npz'), fpr=fpr, tpr=tpr, auc=roc_auc)

    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    np.savez(os.path.join(STATIC_DIR, 'pr_data.npz'), precision=precision, recall=recall)

    return history, metrics


def predict_email(email_content: str) -> float:
    """单封邮件预测"""
    email_tfidf = tfidf.transform([email_content]).toarray()
    prediction = model.predict(email_tfidf)
    return float(prediction[0][0])


@phishing_bp.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    email_content = data.get('email_content', '')
    prob = predict_email(email_content)
    result = 'Phishing' if prob > 0.5 else 'Not Phishing'

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 写入日志文件（保留原有功能）
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{ts}] {result} ({prob:.4f})\n{email_content}\n{'-'*50}\n")

    # 写入数据库
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            insert_sql = """
                INSERT INTO phishing_results (timestamp, result, probability, email_content)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (ts, result, prob, email_content))
        conn.close()
    except Exception as e:
        print(f"写入数据库失败: {e}")

    return jsonify({'result': result, 'probability': prob})


@phishing_bp.route('/metrics', methods=['GET'])
def metrics():
    metrics_file = os.path.join(STATIC_DIR, 'model_metrics.txt')
    if not os.path.exists(metrics_file):
        return jsonify({'error': '模型未训练'}), 400

    metrics = {}
    with open(metrics_file, 'r') as f:
        for line in f:
            key, value = line.strip().split(': ')
            metrics[key] = float(value)
    return jsonify(metrics)


@phishing_bp.route('/retrain', methods=['POST'])
def retrain():
    if os.path.exists(MODEL_FILE):
        os.remove(MODEL_FILE)
    history, metrics = train_and_save_model()
    return jsonify({'status': 'success', 'metrics': metrics})


def init_phishing():
    """
    初始化钓鱼邮件检测
    1. 加载数据和向量化
    2. 尝试加载已有模型
       - 若加载失败，尝试兼容旧版 h5 文件
       - 若不存在模型，训练新模型
    """
    global model
    load_resources()

    if os.path.exists(MODEL_FILE):
        try:
            # 尝试直接加载模型
            model = load_model(MODEL_FILE)
            print("模型加载成功")
        except TypeError as e:
            print(f"模型加载失败: {e}, 尝试兼容旧版 h5 模型...")
            # 兼容旧版 h5 模型，忽略 batch_shape
            from keras.layers import InputLayer

            def fixed_input_layer(**kwargs):
                kwargs.pop('batch_shape', None)
                return InputLayer(**kwargs)

            model = load_model(MODEL_FILE, custom_objects={'InputLayer': fixed_input_layer})
            print("旧版模型兼容加载成功")
        save_model_metrics()  # 只生成 metrics，不重新训练
    else:
        print("未找到模型文件，开始训练新模型...")
        train_and_save_model()
def save_model_metrics():
    """仅计算并保存 metrics，不重新训练模型"""
    if model is not None and X_test is not None:
        y_pred_proba = model.predict(X_test)
        y_pred = (y_pred_proba > 0.5).astype(int)
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred)
        }
        with open(os.path.join(STATIC_DIR, 'model_metrics.txt'), 'w') as f:
            for k, v in metrics.items():
                f.write(f"{k}: {v:.4f}\n")


@phishing_bp.route('/history', methods=['GET'])
def get_prediction_history():
    """
    查询最近的预测结果
    GET 参数: ?limit=10
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                SELECT id, timestamp, result, probability, email_content
                FROM phishing_results
                ORDER BY timestamp DESC
            """
            cursor.execute(sql)
            results = cursor.fetchall()
        conn.close()
        return jsonify({'status': 'success', 'data': results})
    except Exception as e:
        print(f"Error in get_prediction_history: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@phishing_bp.route('/clear', methods=['GET'])
def clear_prediction_results():
    """
    清理预测结果，直接清空整个表。
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "TRUNCATE TABLE phishing_results"
            cursor.execute(sql)
        conn.close()
        return jsonify({'status': 'success', 'message': '预测结果已清理'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@phishing_bp.route('/cron_email_check', methods=['POST'])
def cron_email_check():
    """
    定时检查邮箱中的新邮件并进行钓鱼检测
    """
    try:
        # 从请求体中获取数据
        data = request.get_json()
        minutes = data.get('minutes', 3)  # 默认3分钟
        configs = data.get('configs', [])  # 邮箱配置列表
        
        checked_email_ids = []
        total_phishing_count = 0
        
        # 遍历所有邮箱配置并检查邮件
        for config in configs:
            try:
                # 确保所有必需字段都存在
                required_fields = ['username', 'passwd', 'server', 'port', 'webhook_url']
                for field in required_fields:
                    if field not in config:
                        raise ValueError(f"缺少必需字段: {field}")
                
                result = get_qx_email(
                    minutes,
                    config['username'],
                    config['passwd'],
                    config['server'],
                    config['port'],
                    config['webhook_url']
                )
                
                checked_email_ids.extend(result['email_ids'])
                total_phishing_count += result['phishing_count']
            except Exception as e:
                print(f"检查邮箱 {config.get('username', 'unknown')} 时出错: {e}")
                continue
        
        return jsonify({
            'status': 'success', 
            'checked_email_ids': checked_email_ids,
            'phishing_count': total_phishing_count,
            'total_count': len(checked_email_ids)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
# 获取所有邮箱配置
# 获取所有邮箱配置
@phishing_bp.route('/email_configs', methods=['GET'])
def get_email_configs():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 确保查询包含 passwd 字段
            sql = "SELECT id, username, passwd, server, port, webhook_url FROM email_configs ORDER BY created_at DESC"
            cursor.execute(sql)
            configs = cursor.fetchall()
        conn.close()
        return jsonify(configs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 创建新的邮箱配置
@phishing_bp.route('/email_configs', methods=['POST'])
def create_email_config():
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['username', 'passwd', 'server', 'port', 'webhook_url']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO email_configs (username, passwd, server, port, webhook_url)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data['username'],
                data['passwd'],
                data['server'],
                int(data['port']),
                data['webhook_url']
            ))
            config_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 返回创建的配置（包含ID）
        return jsonify({
            'id': config_id,
            'username': data['username'],
            'server': data['server'],
            'port': int(data['port']),
            'webhook_url': data['webhook_url']
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 更新邮箱配置
@phishing_bp.route('/email_configs/<int:config_id>', methods=['PUT'])
def update_email_config(config_id):
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['username', 'passwd', 'server', 'port', 'webhook_url']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'缺少必需字段: {field}'}), 400
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 检查配置是否存在
            check_sql = "SELECT id FROM email_configs WHERE id = %s"
            cursor.execute(check_sql, (config_id,))
            if not cursor.fetchone():
                return jsonify({'error': '邮箱配置不存在'}), 404
            
            # 更新配置
            sql = """
                UPDATE email_configs 
                SET username = %s, passwd = %s, server = %s, port = %s, webhook_url = %s
                WHERE id = %s
            """
            cursor.execute(sql, (
                data['username'],
                data['passwd'],
                data['server'],
                int(data['port']),
                data['webhook_url'],
                config_id
            ))
        conn.commit()
        conn.close()
        
        # 返回更新后的配置
        return jsonify({
            'id': config_id,
            'username': data['username'],
            'server': data['server'],
            'port': int(data['port']),
            'webhook_url': data['webhook_url']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 删除邮箱配置
@phishing_bp.route('/email_configs/<int:config_id>', methods=['DELETE'])
def delete_email_config(config_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 检查配置是否存在
            check_sql = "SELECT id FROM email_configs WHERE id = %s"
            cursor.execute(check_sql, (config_id,))
            if not cursor.fetchone():
                return jsonify({'error': '邮箱配置不存在'}), 404
            
            # 删除配置
            sql = "DELETE FROM email_configs WHERE id = %s"
            cursor.execute(sql, (config_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': '邮箱配置删除成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500