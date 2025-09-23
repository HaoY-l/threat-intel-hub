<template>
  <div class="log-container">
    <h3 class="log-heading">预测历史记录</h3>
    <div class="log-content">
      <div v-if="logContent.length === 0" class="log-empty">
        暂无历史记录。
      </div>
      <div v-for="(log, index) in logContent" :key="index" class="log-item">
        <p><strong>时间:</strong> {{ log.timestamp }}</p>
        <p><strong>结果:</strong> 
          <span :class="{'phishing-log': log.result === '钓鱼邮件', 'not-phishing-log': log.result === '非钓鱼邮件'}">
            {{ log.result }}
          </span>
          <small> (概率: {{ (log.probability * 100).toFixed(2) }}%)</small>
        </p>
        <p><strong>内容:</strong> {{ log.content.substring(0, 50) }}...</p>
        <hr v-if="index < logContent.length - 1" class="log-divider">
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PredictionLog',
  props: {
    logContent: {
      type: Array,
      required: true
    }
  }
}
</script>

<style scoped>
.log-container {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
}

.log-heading {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: #2e3b4e;
}

.log-content {
  max-height: 300px;
  overflow-y: auto;
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 5px;
  font-family: monospace;
  font-size: 0.9rem;
  text-align: left;
  border: 1px solid #ddd;
}

.log-item {
  margin-bottom: 10px;
}

.phishing-log {
  color: #e74c3c;
  font-weight: bold;
}

.not-phishing-log {
  color: #2ecc71;
  font-weight: bold;
}

.log-divider {
  border: 0;
  border-top: 1px dashed #ccc;
  margin: 10px 0;
}

.log-empty {
  color: #888;
  text-align: center;
}
</style>