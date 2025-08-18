<template>
  <div class="tool-card">
    <h2>WAF 封禁 IP 播报</h2>
    
    <div class="description">
      每天定时或手动触发 WAF 封禁日报播报。
    </div>
    
    <div class="controls">
      <label>
        选择每日播报时间：
        <input
          type="time"
          v-model="scheduledTime"
          @change="saveScheduledTime"
        />
      </label>
      
      <button @click="executeDailyReport" class="execute-button">
        立即执行一次
      </button>
    </div>

    <div class="status">
      <p>播报状态：</p>
      <div v-if="!message" class="default-status">
        <div class="status-info">
          当前播报时间：{{ scheduledTime }}
        </div>
        <div class="status-info">
          定时任务状态：已启动
        </div>
      </div>
      <div v-else :class="['message', statusClass]">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'WafBlockIpCard',
  data() {
    return {
      scheduledTime: '10:00', // 默认每天10点
      message: '',
      statusClass: '',
      timer: null, // 用于存储定时器实例
      messageTimer: null // 用于清除临时消息的定时器
    };
  },
  mounted() {
    this.loadScheduledTime();
    this.setupDailyScheduler();
  },
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer);
    }
    if (this.messageTimer) {
      clearTimeout(this.messageTimer);
    }
  },
  methods: {
    loadScheduledTime() {
      const savedTime = localStorage.getItem('wafReportScheduledTime');
      if (savedTime) {
        this.scheduledTime = savedTime;
      }
    },
    saveScheduledTime() {
      localStorage.setItem('wafReportScheduledTime', this.scheduledTime);
      this.setupDailyScheduler();
      this.showTemporaryMessage('播报时间已更新。', 'success');
    },
    setupDailyScheduler() {
      if (this.timer) {
        clearInterval(this.timer);
      }
      const [hours, minutes] = this.scheduledTime.split(':').map(Number);
      const now = new Date();
      let targetTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hours, minutes, 0, 0);
      if (targetTime.getTime() < now.getTime()) {
        targetTime.setDate(targetTime.getDate() + 1);
      }
      const delay = targetTime.getTime() - now.getTime();
      this.timer = setTimeout(() => {
        this.executeDailyReport();
        this.timer = setInterval(this.executeDailyReport, 24 * 60 * 60 * 1000);
      }, delay);
      console.log(`WAF 播报已设置为每日 ${this.scheduledTime} 执行。`);
    },
    async executeDailyReport() {
      this.message = '正在发送日报请求...';
      this.statusClass = 'info';
      try {
        const response = await axios.get('/api/alert');
        if (response.data.status === 'success') {
          this.showTemporaryMessage('日报发送成功。', 'success');
        } else {
          this.showTemporaryMessage(response.data.message || '日报发送失败。', 'error');
        }
      } catch (error) {
        this.showTemporaryMessage('请求失败，请检查网络或后端服务。', 'error');
        console.error('WAF Daily Report API error:', error);
      }
    },
    showTemporaryMessage(msg, type) {
      this.message = msg;
      this.statusClass = type;
      
      // 清除之前的定时器
      if (this.messageTimer) {
        clearTimeout(this.messageTimer);
      }
      
      // 3秒后清除消息，回到默认状态
      this.messageTimer = setTimeout(() => {
        this.message = '';
        this.statusClass = '';
      }, 3000);
    }
  }
};
</script>

<style scoped>
.tool-card {
  padding: 2rem;
  color: #fff;
  background-color: #2c2c3c;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  flex: 1 1 45%;
  min-width: 300px;
}

h2 {
  margin-top: 0;
  border-bottom: 2px solid #4caf50;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}

.description {
  color: #b0b0c0;
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

.controls {
  margin: 1rem 0;
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.controls label {
  color: #fff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-grow: 1;
}

.controls input {
  width: 150px;
  padding: 0.5rem;
  border-radius: 5px;
  border: 1px solid #444;
  background-color: #333;
  color: #fff;
}

.controls button {
  background-color: #4caf50;
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.controls button:hover {
  background-color: #45a049;
}

.status {
  margin-top: 1rem;
  font-size: 0.9rem;
}

.status p {
  margin-bottom: 0.5rem;
  color: #fff;
}

.default-status {
  background: #333;
  padding: 1rem;
  border-radius: 5px;
}

.status-info {
  color: #b0b0c0;
  margin-bottom: 0.5rem;
}

.status-info:last-child {
  margin-bottom: 0;
}

.message {
  padding: 1rem;
  border-radius: 5px;
  background: #333;
  white-space: pre-wrap;
}

.message.success {
  color: #0f0;
}

.message.error {
  color: #ff5555;
}

.message.info {
  color: #b0b0c0;
}
</style>