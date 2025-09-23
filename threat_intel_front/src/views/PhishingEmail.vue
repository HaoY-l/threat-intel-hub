<template>
  <div class="phishing-email-container">
    <h2>钓鱼邮件检测系统</h2>
    
    <!-- 功能导航栏 -->
    <div class="nav-tabs">
      <button 
        :class="['tab-btn', { active: activeTab === 'predict' }]"
        @click="activeTab = 'predict'"
      >
        邮件检测
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'metrics' }]"
        @click="activeTab = 'metrics'"
      >
        模型性能
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'management' }]"
        @click="activeTab = 'management'"
      >
        模型管理
      </button>
    </div>

    <div class="phishing-content-box">
      <!-- 邮件检测标签页 -->
      <div v-if="activeTab === 'predict'" class="tab-content">
        <div v-if="showResult" class="result-section">
          <h3>分析结果：</h3>
          <div class="result-card">
            <p class="result" :class="{
              'result-phishing': predictionResult === 'Phishing',
              'result-not-phishing': predictionResult === 'Not Phishing'
            }">
              {{ predictionResult === 'Phishing' ? '钓鱼邮件' : '正常邮件' }}
            </p>
            <p class="probability">
              预测概率：{{ (predictionProbability * 100).toFixed(2) }}%
            </p>
            <div class="probability-bar">
              <div 
                class="probability-fill" 
                :class="{ 'danger': predictionProbability > 0.5 }"
                :style="{ width: (predictionProbability * 100) + '%' }"
              ></div>
            </div>
          </div>
          
          <h4>邮件内容：</h4>
          <div class="email-content-display">
            {{ emailContent }}
          </div>
          
          <button class="back-btn" @click="resetForm">
            分析另一封邮件
          </button>
        </div>
        
        <div v-else class="input-section">
          <p class="instructions">请在下方输入邮件内容，系统将使用深度学习模型判断是否为钓鱼邮件【结果小于0.5非钓鱼邮件，反之钓鱼邮件；所展示结果均乘以100%】。</p>
          <textarea 
            v-model="emailContent" 
            rows="15" 
            placeholder="在此处输入邮件内容...&#10;&#10;示例：&#10;Dear Customer,&#10;Your account will be suspended unless you verify your password immediately. Click here to login: http://suspicious-site.com"
            class="email-input"
          ></textarea>
          <div class="button-group">
            <button @click="predictEmail" :disabled="loading || !emailContent.trim()">
              <span v-if="loading">分析中...</span>
              <span v-else>开始检测</span>
            </button>
            <button @click="clearInput" class="secondary-btn">清空内容</button>
          </div>
        </div>

        <div class="section-divider"></div>
        <PredictionLog :log-content="historyLog" />
      </div>

      <!-- 模型性能标签页 -->
      <div v-if="activeTab === 'metrics'" class="tab-content">
        <div class="metrics-section">
          <div class="section-header">
            <h3>模型性能指标</h3>
            <button @click="loadMetrics" :disabled="loading" class="refresh-btn">
              <span v-if="loading">加载中...</span>
              <span v-else>刷新数据</span>
            </button>
          </div>
          
          <div v-if="modelMetrics" class="metrics-grid">
            <div class="metric-card">
              <div class="metric-title">准确率</div>
              <div class="metric-value">{{ (modelMetrics.accuracy * 100).toFixed(2) }}%</div>
              <div class="metric-desc">模型预测正确的比例</div>
            </div>
            <div class="metric-card">
              <div class="metric-title">精确率</div>
              <div class="metric-value">{{ (modelMetrics.precision * 100).toFixed(2) }}%</div>
              <div class="metric-desc">预测为钓鱼邮件中真正是钓鱼邮件的比例</div>
            </div>
            <div class="metric-card">
              <div class="metric-title">召回率</div>
              <div class="metric-value">{{ (modelMetrics.recall * 100).toFixed(2) }}%</div>
              <div class="metric-desc">实际钓鱼邮件被正确识别的比例</div>
            </div>
            <div class="metric-card">
              <div class="metric-title">F1分数</div>
              <div class="metric-value">{{ (modelMetrics.f1_score * 100).toFixed(2) }}%</div>
              <div class="metric-desc">精确率和召回率的调和平均</div>
            </div>
          </div>
          
          <div v-else-if="!loading" class="no-metrics">
            <p>暂无模型性能数据，请先训练模型或检查模型状态。</p>
          </div>
          
          <div v-if="loading" class="loading-state">
            <p>正在加载性能指标...</p>
          </div>
        </div>
      </div>

      <!-- 模型管理标签页 -->
      <div v-if="activeTab === 'management'" class="tab-content">
        <div class="management-section">
          <h3>模型管理</h3>
          
          <div class="management-grid">
            <div class="management-card">
              <h4>重新训练模型</h4>
              <p>使用最新数据重新训练模型，提升检测准确性。训练过程可能需要几分钟时间。</p>
              <button 
                @click="retrainModel" 
                :disabled="retraining"
                class="retrain-btn"
              >
                <span v-if="retraining">训练中...</span>
                <span v-else>开始重新训练</span>
              </button>
              <div v-if="retrainingStatus" class="training-status">
                {{ retrainingStatus }}
              </div>
            </div>
            
            <div class="management-card">
              <h4>模型信息</h4>
              <div class="model-info">
                <p><strong>模型类型：</strong>深度神经网络</p>
                <p><strong>特征提取：</strong>TF-IDF向量化</p>
                <p><strong>训练数据：</strong>spam_assassin.csv</p>
                <p><strong>最大特征数：</strong>5000</p>
                <p><strong>网络结构：</strong>128→64→1层</p>
              </div>
            </div>
            
            <div class="management-card">
              <h4>系统状态</h4>
              <div class="system-status">
                <div class="status-item">
                  <span class="status-label">模型状态：</span>
                  <span :class="['status-value', modelStatus.toLowerCase()]">
                    {{ modelStatus }}
                  </span>
                </div>
                <div class="status-item">
                  <span class="status-label">API连接：</span>
                  <span :class="['status-value', apiStatus.toLowerCase()]">
                    {{ apiStatus }}
                  </span>
                </div>
              </div>
              <button @click="checkSystemStatus" class="check-btn">检查状态</button>
            </div>
          </div>
          
          <!-- 最近训练结果 -->
          <div v-if="lastTrainingResult" class="training-result">
            <h4>最近训练结果</h4>
            <div class="result-grid">
              <div class="result-item">
                <span class="label">准确率：</span>
                <span class="value">{{ (lastTrainingResult.accuracy * 100).toFixed(2) }}%</span>
              </div>
              <div class="result-item">
                <span class="label">精确率：</span>
                <span class="value">{{ (lastTrainingResult.precision * 100).toFixed(2) }}%</span>
              </div>
              <div class="result-item">
                <span class="label">召回率：</span>
                <span class="value">{{ (lastTrainingResult.recall * 100).toFixed(2) }}%</span>
              </div>
              <div class="result-item">
                <span class="label">F1分数：</span>
                <span class="value">{{ (lastTrainingResult.f1_score * 100).toFixed(2) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PredictionLog from '@/components/phishemail/PredictionLog.vue';
import axios from 'axios';

export default {
  name: 'PhishingEmail',
  components: {
    PredictionLog
  },
  data() {
    return {
      activeTab: 'predict', // predict, metrics, management
      emailContent: '',
      predictionResult: '',
      predictionProbability: 0,
      showResult: false,
      historyLog: [],
      loading: false,
      retraining: false,
      retrainingStatus: '',
      modelMetrics: null,
      lastTrainingResult: null,
      modelStatus: '未知',
      apiStatus: '未知',
      // API基础URL，根据你的后端地址修改
      apiBaseUrl: 'http://localhost:8891/api/phishing'
    }
  },
  mounted() {
    this.checkSystemStatus();
    this.loadHistoryFromStorage();
  },
  methods: {
    // 邮件预测
    async predictEmail() {
      if (!this.emailContent.trim()) {
        alert('请输入邮件内容！');
        return;
      }
      
      this.loading = true;
      try {
        const response = await axios.post(`${this.apiBaseUrl}/predict`, {
          email_content: this.emailContent
        });
        
        this.predictionResult = response.data.result;
        this.predictionProbability = response.data.probability;
        
        // 更新历史记录
        const timestamp = new Date().toLocaleString();
        const logEntry = {
          timestamp,
          content: this.emailContent,
          result: this.predictionResult,
          probability: this.predictionProbability
        };
        
        this.historyLog.unshift(logEntry);
        this.saveHistoryToStorage();
        
        this.showResult = true;
        
        // 如果是钓鱼邮件，弹出警告
        if (this.predictionResult === 'Phishing') {
          alert("⚠️ 警告：该邮件被判定为钓鱼邮件，请勿点击其中的链接或下载附件！");
        }
        
      } catch (error) {
        console.error('预测失败:', error);
        alert('预测失败，请检查网络连接或联系管理员。');
      } finally {
        this.loading = false;
      }
    },
    
    // 加载模型性能指标
    async loadMetrics() {
      this.loading = true;
      try {
        const response = await axios.get(`${this.apiBaseUrl}/metrics`);
        this.modelMetrics = response.data;
      } catch (error) {
        console.error('加载指标失败:', error);
        alert('加载模型性能指标失败，请检查模型是否已训练。');
        this.modelMetrics = null;
      } finally {
        this.loading = false;
      }
    },
    
    // 重新训练模型
    async retrainModel() {
      if (!confirm('重新训练模型将花费几分钟时间，确定要继续吗？')) {
        return;
      }
      
      this.retraining = true;
      this.retrainingStatus = '正在初始化训练...';
      
      try {
        const response = await axios.post(`${this.apiBaseUrl}/retrain`);
        
        if (response.data.status === 'success') {
          this.retrainingStatus = '训练完成！';
          this.lastTrainingResult = response.data.metrics;
          alert('模型重新训练成功！');
          
          // 刷新模型指标
          this.loadMetrics();
        } else {
          throw new Error('训练失败');
        }
        
      } catch (error) {
        console.error('重新训练失败:', error);
        this.retrainingStatus = '训练失败，请重试。';
        alert('模型重新训练失败，请检查后端服务。');
      } finally {
        this.retraining = false;
        // 3秒后清除状态信息
        setTimeout(() => {
          this.retrainingStatus = '';
        }, 3000);
      }
    },
    
    // 检查系统状态
    async checkSystemStatus() {
      try {
        // 尝试获取指标来检查模型状态
        const response = await axios.get(`${this.apiBaseUrl}/metrics`);
        this.modelStatus = '正常';
        this.apiStatus = '连接正常';
      } catch (error) {
        if (error.response && error.response.status === 400) {
          this.modelStatus = '未训练';
          this.apiStatus = '连接正常';
        } else {
          this.modelStatus = '异常';
          this.apiStatus = '连接失败';
        }
      }
    },
    
    // 重置表单
    resetForm() {
      this.emailContent = '';
      this.showResult = false;
      this.predictionResult = '';
      this.predictionProbability = 0;
    },
    
    // 清空输入
    clearInput() {
      this.emailContent = '';
    },
    
    // 保存历史记录到本地存储
    saveHistoryToStorage() {
      try {
        localStorage.setItem('phishing_history', JSON.stringify(this.historyLog.slice(0, 20))); // 只保存最近20条
      } catch (error) {
        console.warn('保存历史记录失败:', error);
      }
    },
    
    // 从本地存储加载历史记录
    loadHistoryFromStorage() {
      try {
        const saved = localStorage.getItem('phishing_history');
        if (saved) {
          this.historyLog = JSON.parse(saved);
        }
      } catch (error) {
        console.warn('加载历史记录失败:', error);
      }
    }
  }
}
</script>

<style scoped>
.phishing-email-container {
  height: 100%;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.nav-tabs {
  display: flex;
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.tab-btn {
  flex: 1;
  padding: 12px 20px;
  background-color: #ecf0f1;
  color: #2c3e50;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
}

.tab-btn:hover {
  background-color: #d5dbdb;
}

.tab-btn.active {
  background-color: #3498db;
  color: white;
}

.phishing-content-box {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 30px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.tab-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

h2 {
  font-size: 2.5rem;
  color: #fff;
  text-align: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

h3, h4 {
  font-size: 1.5rem;
  color: #2e3b4e;
  margin-bottom: 15px;
}

/* 邮件检测相关样式 */
.instructions {
  font-size: 1.1rem;
  color: #555;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-left: 5px solid #4CAF50;
  border-radius: 4px;
  flex-shrink: 0;
}

.input-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.email-input {
  width: 100%;
  padding: 12px;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin: 10px 0;
  resize: vertical;
  box-sizing: border-box;
  min-height: 120px;     /* 原来的200改小 */
  max-height: 250px;     /* 限制最大高度 */
  overflow-y: auto;      /* 超出滚动 */
  flex: unset;           /* 不占满剩余空间 */
}

.button-group {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

button {
  background-color: #4CAF50;
  color: white;
  font-size: 1.1rem;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  flex: 1;
}

button:hover:not(:disabled) {
  background-color: #45a049;
  transform: translateY(-1px);
}

button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
  transform: none;
}

.secondary-btn {
  background-color: #95a5a6;
}

.secondary-btn:hover:not(:disabled) {
  background-color: #7f8c8d;
}

.result-section {
  text-align: center;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.result-card {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.result {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 20px 0;
}

.result-phishing {
  color: #e74c3c;
}

.result-not-phishing {
  color: #2ecc71;
}

.probability {
  font-size: 1.3rem;
  color: #555;
  margin-bottom: 15px;
}

.probability-bar {
  width: 100%;
  height: 8px;
  background-color: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
}

.probability-fill {
  height: 100%;
  background-color: #2ecc71;
  transition: width 0.5s ease;
  border-radius: 4px;
}

.probability-fill.danger {
  background-color: #e74c3c;
}

.email-content-display {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
  text-align: left;
  border-left: 4px solid #3498db;
  white-space: pre-wrap;
  flex: 1;
  overflow-y: auto;
  min-height: 120px;
  font-family: monospace;
  line-height: 1.4;
}

.back-btn {
  background-color: #3498db;
  margin-top: 20px;
  flex-shrink: 0;
  max-width: 200px;
  align-self: center;
}

.back-btn:hover:not(:disabled) {
  background-color: #2980b9;
}

/* 模型性能相关样式 */
.metrics-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.refresh-btn {
  background-color: #3498db;
  max-width: 120px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  flex: 1;
}

.metric-card {
  background-color: #f8f9fa;
  padding: 25px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3498db;
}

.metric-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
}

.metric-value {
  font-size: 2.2rem;
  font-weight: bold;
  color: #3498db;
  margin-bottom: 8px;
}

.metric-desc {
  font-size: 0.9rem;
  color: #7f8c8d;
  line-height: 1.4;
}

.no-metrics {
  text-align: center;
  color: #7f8c8d;
  font-size: 1.1rem;
  margin-top: 50px;
}

.loading-state {
  text-align: center;
  color: #3498db;
  font-size: 1.1rem;
  margin-top: 50px;
}

/* 模型管理相关样式 */
.management-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.management-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.management-card {
  background-color: #f8f9fa;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.management-card h4 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 1.3rem;
}

.management-card p {
  color: #7f8c8d;
  line-height: 1.6;
  margin-bottom: 20px;
}

.retrain-btn {
  background-color: #e67e22;
  width: 100%;
}

.retrain-btn:hover:not(:disabled) {
  background-color: #d35400;
}

.training-status {
  margin-top: 15px;
  padding: 10px;
  background-color: #d5e8d4;
  border-radius: 4px;
  color: #27ae60;
  font-weight: 500;
  text-align: center;
}

.model-info {
  text-align: left;
}

.model-info p {
  margin-bottom: 8px;
  color: #2c3e50;
}

.system-status {
  margin-bottom: 20px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #ecf0f1;
}

.status-label {
  font-weight: 500;
  color: #2c3e50;
}

.status-value {
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 0.9rem;
}

.status-value.正常 {
  background-color: #d5e8d4;
  color: #27ae60;
}

.status-value.连接正常 {
  background-color: #d5e8d4;
  color: #27ae60;
}

.status-value.未训练 {
  background-color: #ffeaa7;
  color: #f39c12;
}

.status-value.异常, .status-value.连接失败 {
  background-color: #fadbd8;
  color: #e74c3c;
}

.check-btn {
  background-color: #9b59b6;
  width: 100%;
}

.check-btn:hover:not(:disabled) {
  background-color: #8e44ad;
}

.training-result {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #27ae60;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: white;
  border-radius: 4px;
}

.result-item .label {
  font-weight: 500;
  color: #2c3e50;
}

.result-item .value {
  font-weight: 600;
  color: #27ae60;
}

.section-divider {
  height: 1px;
  background-color: #ddd;
  margin: 30px 0;
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .phishing-email-container {
    padding: 15px;
  }
  
  .phishing-content-box {
    padding: 20px;
  }
  
  h2 {
    font-size: 2rem;
  }
  
  .nav-tabs {
    flex-direction: column;
  }
  
  .metrics-grid,
  .management-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .result-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .phishing-email-container {
    padding: 10px;
  }
  
  .phishing-content-box {
    padding: 15px;
  }
  
  h2 {
    font-size: 1.8rem;
  }
  
  .result {
    font-size: 2rem;
  }
  
  .button-group {
    flex-direction: column;
  }
}

.prediction-log-container {
  max-height: 300px;  
  overflow-y: auto;   
}
</style>