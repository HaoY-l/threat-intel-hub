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
        :class="['tab-btn', { active: activeTab === 'autodetect' }]"
        @click="activeTab = 'autodetect'"
      >
        自动检测
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

      <!-- 自动检测标签页 -->
      <div v-if="activeTab === 'autodetect'" class="tab-content">
        <div class="autodetect-section">
          <h3>自动邮件检测</h3>
          
          <!-- 自动检测配置 -->
          <div class="autodetect-config">
            <div class="config-card">
              <h4>定时检测配置</h4>
              <div class="config-row">
                <label for="interval">检测间隔（分钟）：</label>
                <input 
                  type="number" 
                  id="interval" 
                  v-model.number="autoCheckInterval" 
                  min="1" 
                  max="1440" 
                  class="interval-input"
                  :disabled="isAutoCheckRunning"
                />
                <span class="unit">分钟</span>
              </div>
              
              <div class="config-row">
                <label for="timeRange">检查邮件时间范围：</label>
                <select 
                  id="timeRange" 
                  v-model="emailTimeRange" 
                  class="time-range-select"
                  :disabled="isAutoCheckRunning"
                >
                  <option value="same">与检测间隔相同</option>
                  <option value="custom">自定义</option>
                </select>
                
                <input 
                  v-if="emailTimeRange === 'custom'"
                  type="number" 
                  v-model.number="customTimeRange" 
                  min="1" 
                  max="1440" 
                  class="interval-input custom-range-input"
                  :disabled="isAutoCheckRunning"
                />
                <span v-if="emailTimeRange === 'custom'" class="unit">分钟</span>
              </div>
              
              <div class="control-buttons">
                <button 
                  @click="startAutoCheck" 
                  :disabled="isAutoCheckRunning || autoCheckInterval < 1"
                  class="start-btn"
                >
                  开始自动检测
                </button>
                <button 
                  @click="stopAutoCheck" 
                  :disabled="!isAutoCheckRunning"
                  class="stop-btn"
                >
                  停止自动检测
                </button>
              </div>
            </div>
            
            <!-- 状态显示 -->
            <div class="status-card">
              <h4>检测状态</h4>
              <div class="status-info">
                <div class="status-item">
                  <span class="label">当前状态：</span>
                  <span :class="['status', isAutoCheckRunning ? 'running' : 'stopped']">
                    {{ isAutoCheckRunning ? '运行中' : '已停止' }}
                  </span>
                </div>
                <div class="status-item" v-if="isAutoCheckRunning">
                  <span class="label">检测间隔：</span>
                  <span class="value">{{ autoCheckInterval }} 分钟</span>
                </div>
                <div class="status-item" v-if="isAutoCheckRunning">
                  <span class="label">下次检测：</span>
                  <span class="value">{{ nextCheckTime }}</span>
                </div>
                <div class="status-item">
                  <span class="label">总检测次数：</span>
                  <span class="value">{{ totalCheckCount }}</span>
                </div>
                <div class="status-item">
                  <span class="label">发现钓鱼邮件：</span>
                  <span class="value phishing-count">{{ phishingEmailCount }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 自动检测日志 -->
          <div class="autodetect-log">
            <div class="log-header">
              <h4>检测日志</h4>
              <button @click="clearAutoDetectLog" class="clear-log-btn">清空日志</button>
            </div>
            <div class="log-content" ref="autoLogContent">
              <div 
                v-for="(log, index) in autoDetectLogs" 
                :key="index"
                :class="['log-item', log.type]"
              >
                <span class="log-time">{{ log.timestamp }}</span>
                <span class="log-message">{{ log.message }}</span>
                <span v-if="log.emailIds && log.emailIds.length > 0" class="email-count">
                  （检测到 {{ log.emailIds.length }} 封邮件）
                </span>
              </div>
              <div v-if="autoDetectLogs.length === 0" class="no-logs">
                暂无检测日志
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 模型性能标签页 -->
      <div v-if="activeTab === 'metrics'" class="tab-content">
        <div class="metrics-section">
          <div class="section-header">
            <h3>模型性能指标</h3>
            <button @click="loadMetrics" :disabled="loading" class="refresh-btn">
              <span v-if="loading">加载中...</span>
              <span v-else">刷新数据</span>
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
      activeTab: 'predict', // predict, autodetect, metrics, management
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
      
      // 自动检测相关
      autoCheckInterval: 30, // 默认30分钟
      emailTimeRange: 'same', // 'same' 或 'custom'
      customTimeRange: 30,
      isAutoCheckRunning: false,
      autoCheckTimer: null,
      nextCheckTime: '',
      totalCheckCount: 0,
      phishingEmailCount: 0,
      autoDetectLogs: [],
      
      // API基础URL，根据你的后端地址修改
      apiBaseUrl: 'http://localhost:8891/api/phishing'
    }
  },
  computed: {
    actualTimeRange() {
      return this.emailTimeRange === 'custom' ? this.customTimeRange : this.autoCheckInterval;
    }
  },
  mounted() {
    this.checkSystemStatus();
    this.loadHistoryFromStorage();
    this.loadAutoDetectSettings();
  },
  beforeUnmount() {
    this.stopAutoCheck();
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
    
    // 启动自动检测
    startAutoCheck() {
      if (this.autoCheckInterval < 1) {
        alert('检测间隔必须大于0分钟！');
        return;
      }
      
      this.isAutoCheckRunning = true;
      this.addAutoDetectLog('info', '自动检测已启动');
      
      // 立即执行一次检测
      this.performAutoCheck();
      
      // 设置定时器
      this.autoCheckTimer = setInterval(() => {
        this.performAutoCheck();
      }, this.autoCheckInterval * 60 * 1000); // 转换为毫秒
      
      this.updateNextCheckTime();
      this.saveAutoDetectSettings();
    },
    
    // 停止自动检测
    stopAutoCheck() {
      if (this.autoCheckTimer) {
        clearInterval(this.autoCheckTimer);
        this.autoCheckTimer = null;
      }
      this.isAutoCheckRunning = false;
      this.nextCheckTime = '';
      this.addAutoDetectLog('info', '自动检测已停止');
      this.saveAutoDetectSettings();
    },
    
    // 执行自动检测
    async performAutoCheck() {
      try {
        this.addAutoDetectLog('info', `开始检测过去${this.actualTimeRange}分钟内的邮件...`);
        
        const response = await axios.get(`${this.apiBaseUrl}/cron_email_check/${this.actualTimeRange}`);
        
        this.totalCheckCount++;
        
        if (response.data.status === 'success') {
          const emailIds = response.data.checked_email_ids || [];
          
          if (emailIds.length === 0) {
            this.addAutoDetectLog('success', '未发现新邮件');
          } else {
            this.addAutoDetectLog('success', `检测完成`, emailIds);
            
            // 这里可以根据实际需要统计钓鱼邮件数量
            // 由于后端接口可能需要扩展返回钓鱼邮件统计，这里先简单处理
            // this.phishingEmailCount += phishingCount;
          }
        } else {
          this.addAutoDetectLog('error', `检测失败: ${response.data.message}`);
        }
        
      } catch (error) {
        console.error('自动检测失败:', error);
        this.addAutoDetectLog('error', `检测出错: ${error.response?.data?.message || error.message}`);
      }
      
      if (this.isAutoCheckRunning) {
        this.updateNextCheckTime();
      }
    },
    
    // 更新下次检测时间
    updateNextCheckTime() {
      const nextTime = new Date(Date.now() + this.autoCheckInterval * 60 * 1000);
      this.nextCheckTime = nextTime.toLocaleString();
    },
    
    // 添加自动检测日志
    addAutoDetectLog(type, message, emailIds = null) {
      const log = {
        timestamp: new Date().toLocaleString(),
        type, // 'info', 'success', 'error'
        message,
        emailIds
      };
      
      this.autoDetectLogs.unshift(log);
      
      // 只保留最近50条日志
      if (this.autoDetectLogs.length > 50) {
        this.autoDetectLogs = this.autoDetectLogs.slice(0, 50);
      }
      
      // 自动滚动到最新日志
      this.$nextTick(() => {
        if (this.$refs.autoLogContent) {
          this.$refs.autoLogContent.scrollTop = 0;
        }
      });
      
      this.saveAutoDetectSettings();
    },
    
    // 清空自动检测日志
    clearAutoDetectLog() {
      if (confirm('确定要清空所有检测日志吗？')) {
        this.autoDetectLogs = [];
        this.saveAutoDetectSettings();
      }
    },
    
    // 保存自动检测设置
    saveAutoDetectSettings() {
      const settings = {
        autoCheckInterval: this.autoCheckInterval,
        emailTimeRange: this.emailTimeRange,
        customTimeRange: this.customTimeRange,
        totalCheckCount: this.totalCheckCount,
        phishingEmailCount: this.phishingEmailCount,
        autoDetectLogs: this.autoDetectLogs.slice(0, 20) // 只保存最近20条
      };
      
      try {
        localStorage.setItem('auto_detect_settings', JSON.stringify(settings));
      } catch (error) {
        console.warn('保存自动检测设置失败:', error);
      }
    },
    
    // 加载自动检测设置
    loadAutoDetectSettings() {
      try {
        const saved = localStorage.getItem('auto_detect_settings');
        if (saved) {
          const settings = JSON.parse(saved);
          this.autoCheckInterval = settings.autoCheckInterval || 30;
          this.emailTimeRange = settings.emailTimeRange || 'same';
          this.customTimeRange = settings.customTimeRange || 30;
          this.totalCheckCount = settings.totalCheckCount || 0;
          this.phishingEmailCount = settings.phishingEmailCount || 0;
          this.autoDetectLogs = settings.autoDetectLogs || [];
        }
      } catch (error) {
        console.warn('加载自动检测设置失败:', error);
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
  background-color: #f4f7f9;
}

h2 {
  font-size: 2.5rem;
  color: #34495e;
  text-align: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.nav-tabs {
  display: flex;
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
  font-weight: 600;
}

.tab-btn:hover {
  background-color: #d5dbdb;
}

.tab-btn.active {
  background-color: #3498db;
  color: white;
  font-weight: bold;
}

.phishing-content-box {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
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

h3, h4 {
  font-size: 1.5rem;
  color: #2e3b4e;
  margin-bottom: 15px;
}

/* 邮件检测 */
.input-section, .result-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.instructions {
  color: #7f8c8d;
  margin-bottom: 20px;
  line-height: 1.6;
}

.email-input {
  width: 100%;
  padding: 15px;
  border: 1px solid #bdc3c7;
  border-radius: 6px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 1rem;
  resize: vertical;
  flex: 1;
  box-sizing: border-box;
  transition: border-color 0.3s;
}

.email-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 5px rgba(52, 152, 219, 0.5);
}

.button-group {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.button-group button {
  padding: 12px 25px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.1s;
  font-weight: 600;
}

.button-group button:disabled {
  background-color: #b9c1c6;
  cursor: not-allowed;
}

.button-group button:hover:not(:disabled) {
  transform: translateY(-2px);
}

.button-group button:first-child {
  background-color: #3498db;
  color: white;
}

.button-group button:first-child:hover:not(:disabled) {
  background-color: #2980b9;
}

.secondary-btn {
  background-color: #ecf0f1;
  color: #2c3e50;
}

.secondary-btn:hover:not(:disabled) {
  background-color: #d5dbdb;
}

.result-section {
  display: flex;
  flex-direction: column;
}

.result-card {
  background-color: #f8f9fa;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
  margin-bottom: 20px;
}

.result {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.result-phishing {
  color: #e74c3c;
}

.result-not-phishing {
  color: #27ae60;
}

.probability {
  font-size: 1.2rem;
  color: #7f8c8d;
  margin-bottom: 15px;
}

.probability-bar {
  width: 80%;
  height: 15px;
  background-color: #e0e0e0;
  border-radius: 8px;
  margin: 0 auto;
  overflow: hidden;
}

.probability-fill {
  height: 100%;
  background-color: #27ae60;
  transition: width 0.5s ease-in-out;
  border-radius: 8px;
}

.probability-fill.danger {
  background-color: #e74c3c;
}

.email-content-display {
  white-space: pre-wrap;
  background-color: #fdfdfd;
  border: 1px solid #dfe6e9;
  border-radius: 6px;
  padding: 15px;
  flex: 1;
  overflow-y: auto;
  margin-bottom: 20px;
  line-height: 1.6;
}

.back-btn {
  padding: 12px 25px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: background-color 0.3s;
  align-self: center;
}

.back-btn:hover {
  background-color: #2980b9;
}

.section-divider {
  height: 1px;
  background-color: #ecf0f1;
  margin: 20px 0;
}

/* 自动检测相关样式 */
.autodetect-section {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.autodetect-config {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.config-card, .status-card {
  background-color: #f8f9fa;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.config-card h4, .status-card h4 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.3rem;
}

.config-row {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
}

.config-row label {
  min-width: 140px;
  font-weight: 500;
  color: #2c3e50;
}

.interval-input, .time-range-select {
  padding: 8px 12px;
  border: 1px solid #bdc3c7;
  border-radius: 6px;
  font-size: 1rem;
}

.interval-input {
  width: 80px;
}

.custom-range-input {
  width: 80px;
}

.unit {
  color: #7f8c8d;
}

.control-buttons {
  display: flex;
  gap: 15px;
  margin-top: 10px;
}

.control-buttons button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.control-buttons button:disabled {
  background-color: #b9c1c6;
  cursor: not-allowed;
}

.start-btn {
  background-color: #2ecc71;
  color: white;
}

.start-btn:hover:not(:disabled) {
  background-color: #27ae60;
}

.stop-btn {
  background-color: #e74c3c;
  color: white;
}

.stop-btn:hover:not(:disabled) {
  background-color: #c0392b;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-item .label {
  color: #7f8c8d;
}

.status-item .value {
  font-weight: bold;
}

.status.running {
  color: #2ecc71;
}

.status.stopped {
  color: #e74c3c;
}

.phishing-count {
  color: #e74c3c;
  font-size: 1.1rem;
}

.autodetect-log {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fdfdfd;
  border: 1px solid #dfe6e9;
  border-radius: 6px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  border-bottom: 1px solid #dfe6e9;
}

.log-header h4 {
  margin-bottom: 0;
}

.clear-log-btn {
  background-color: #e74c3c;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.clear-log-btn:hover {
  background-color: #c0392b;
}

.log-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column-reverse;
}

.log-item {
  margin-bottom: 10px;
  padding: 12px;
  border-left: 5px solid;
  border-radius: 4px;
  background-color: #fafafa;
  word-wrap: break-word;
}

.log-item.info {
  border-left-color: #3498db;
}

.log-item.success {
  border-left-color: #2ecc71;
}

.log-item.error {
  border-left-color: #e74c3c;
}

.log-time {
  font-size: 0.8rem;
  color: #95a5a6;
  display: block;
  margin-bottom: 5px;
}

.log-message {
  font-weight: 500;
}

.email-count {
  font-style: italic;
  color: #95a5a6;
  margin-left: 10px;
}

.no-logs {
  text-align: center;
  color: #95a5a6;
  font-style: italic;
  padding: 20px;
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
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #2980b9;
}

.refresh-btn:disabled {
  background-color: #b9c1c6;
  cursor: not-allowed;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  flex: 1;
}

.metric-card {
  background-color: #f8f9fa;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.metric-title {
  font-size: 1.2rem;
  color: #34495e;
  font-weight: 600;
  margin-bottom: 10px;
}

.metric-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #3498db;
  margin-bottom: 10px;
}

.metric-desc {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.no-metrics, .loading-state {
  text-align: center;
  color: #7f8c8d;
  padding: 50px 0;
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
  flex: 1;
  align-content: flex-start;
}

.management-card {
  background-color: #f8f9fa;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.management-card h4 {
  font-size: 1.3rem;
  color: #34495e;
  margin-bottom: 15px;
}

.retrain-btn, .check-btn {
  padding: 12px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.retrain-btn {
  background-color: #e67e22;
  color: white;
}

.retrain-btn:hover:not(:disabled) {
  background-color: #d35400;
}

.retrain-btn:disabled {
  background-color: #b9c1c6;
  cursor: not-allowed;
}

.training-status {
  margin-top: 15px;
  font-style: italic;
  color: #2c3e50;
}

.model-info, .system-status {
  margin-top: 15px;
}

.model-info p, .system-status .status-item {
  margin-bottom: 10px;
  color: #555;
}

.model-info strong {
  color: #333;
}

.system-status {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.system-status .status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-label {
  font-weight: 500;
  color: #7f8c8d;
}

.status-value {
  font-weight: bold;
}

.status-value.正常 {
  color: #2ecc71;
}

.status-value.未训练 {
  color: #f1c40f;
}

.status-value.异常, .status-value.连接失败 {
  color: #e74c3c;
}

.check-btn {
  background-color: #95a5a6;
  color: white;
  margin-top: 15px;
}

.check-btn:hover {
  background-color: #7f8c8d;
}

.training-result {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #dfe6e9;
}

.training-result h4 {
  margin-bottom: 20px;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #f0f3f5;
  border-radius: 6px;
}

.result-item .label {
  font-weight: 500;
  color: #555;
}

.result-item .value {
  font-weight: bold;
  color: #34495e;
}
</style>