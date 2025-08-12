<template>
  <div class="tool-card">
    <h2>定时公众号发布</h2>

    <div class="controls">
      <label>
        间隔：
        <input type="number" v-model.number="interval.days" min="0" /> 天
        <input type="number" v-model.number="interval.hours" min="0" max="23" /> 小时
        <input type="number" v-model.number="interval.minutes" min="0" max="59" /> 分钟
      </label>

      <button @click="startTimer" :disabled="isRunning">启动任务</button>
      <button @click="stopTimer" :disabled="!isRunning">停止任务</button>
      <button @click="runNow">立即发布一次</button>
    </div>

    <div class="status">
      <p>定时任务状态：<strong>{{ isRunning ? '运行中 🟢' : '已停止 🔴' }}</strong></p>
      <p>最近发布时间：<strong>{{ lastRunTime || '暂无' }}</strong></p>
      <p>最近接口响应：</p>
      <pre>{{ lastResponse }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WeChatPublisherCard',
  data() {
    return {
      interval: {
        days: 0,
        hours: 0,
        minutes: 10
      },
      timerId: null,
      isRunning: false,
      lastRunTime: '',
      lastResponse: ''
    }
  },
  computed: {
    totalIntervalMs() {
      const { days, hours, minutes } = this.interval
      return (
        ((days * 24 + hours) * 60 + minutes) * 60 * 1000
      )
    }
  },
  methods: {
    async callPublishAPI() {
      try {
        const res = await fetch('/api/wxgzh', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        const data = await res.json()
        this.lastResponse = JSON.stringify(data, null, 2)
        this.lastRunTime = new Date().toLocaleString()
      } catch (err) {
        this.lastResponse = '❌ 请求失败: ' + err.message
      }
    },
    startTimer() {
      if (this.totalIntervalMs <= 0) {
        alert("时间间隔必须大于0")
        return
      }
      if (this.timerId) return

      this.isRunning = true
      this.callPublishAPI() // 立即执行一次
      this.timerId = setInterval(() => {
        this.callPublishAPI()
      }, this.totalIntervalMs)
    },
    stopTimer() {
      if (this.timerId) {
        clearInterval(this.timerId)
        this.timerId = null
        this.isRunning = false
      }
    },
    runNow() {
      this.callPublishAPI()
    }
  },
  beforeUnmount() {
    this.stopTimer()
  }
}
</script>

<style scoped>
/* 卡片基础样式 */
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

.controls {
  margin: 1rem 0;
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.controls input {
  width: 60px;
  padding: 0.3rem;
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

.controls button:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}

.controls button:hover:not(:disabled) {
  background-color: #45a049;
}

.status {
  margin-top: 1rem;
  font-size: 0.9rem;
}

.status pre {
  background: #333;
  padding: 0.5rem;
  border-radius: 5px;
  white-space: pre-wrap;
  color: #0f0;
}
</style>