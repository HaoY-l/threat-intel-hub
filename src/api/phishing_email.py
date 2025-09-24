from datetime import datetime
import os
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
    """定义深度学习模型"""
    model = Sequential([
        Dense(128, activation='relu', input_dim=input_dim),
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
    global model
    load_resources()
    if os.path.exists(MODEL_FILE):
        model = load_model(MODEL_FILE)
        save_model_metrics()  # 只生成 metrics，不重新训练
    else:
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
    
@phishing_bp.route('/cron_email_check/<int:minutes>', methods=['GET'])
def cron_email_check(minutes):
    """
    定时检查邮箱中的新邮件并进行钓鱼检测
    """
    try:
        # 这里调用你的main函数（假设你把main函数重命名为get_qx_email或者导入了）
        email_ids = get_qx_email(minutes)  # 或者 get_qx_email(minutes)
        return jsonify({'status': 'success', 'checked_email_ids': email_ids})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500