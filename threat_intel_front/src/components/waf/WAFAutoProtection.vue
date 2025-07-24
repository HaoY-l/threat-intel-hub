<template>
  <div class="monitor-card auto-protection">
    <div class="card-header">
      <div class="card-title">
        <i class="card-icon fa fa-bolt"></i>
        <span>自动封禁日志</span>
      </div>
      <div class="card-actions">
        <div class="status-indicator" :class="{ active: logs.length > 0 }"></div>
      </div>
    </div>
    <div class="card-content">
      <div class="log-list">
        <div class="log-item header">
          <div class="log-col ip">IP 地址</div>
          <div class="log-col action">操作</div>
          <div class="log-col reason">原因</div>
          <div class="log-col score">评分</div>
          <div class="log-col time">时间</div>
        </div>
        <div v-if="logs.length === 0" class="no-logs">
          暂无自动封禁日志记录。
        </div>
        <div v-else class="log-scroll-area">
          <div v-for="log in logs" :key="log.id" class="log-item">
            <div class="log-col ip" :title="log.ip">{{ log.ip }}</div>
            <div class="log-col action" :class="getActionClass(log.action)" :title="getActionText(log.action)">{{ getActionText(log.action) }}</div>
            <div class="log-col reason" :title="log.reason || '无'">{{ log.reason || '无' }}</div>
            <div class="log-col score" :title="log.reputation_score !== null ? log.reputation_score.toString() : 'N/A'">{{ log.reputation_score !== null ? log.reputation_score : 'N/A' }}</div>
            <div class="log-col time" :title="formatTime(log.action_time)">{{ formatTime(log.action_time) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import moment from 'moment' 

export default {
  name: 'WAFAutoProtectionLogs', 
  data() {
    return {
      logs: [] 
    }
  },
  mounted() {
    this.fetchProtectedIpLogs();
  },
  methods: {
    async fetchProtectedIpLogs() {
      try {
        const response = await axios.get('/api/protected_ip'); 
        this.logs = response.data; 
      } catch (error) {
        console.error('获取自动封禁日志失败:', error);
        this.logs = []; 
      }
    },
    formatTime(timestamp) {
      if (timestamp) {
        // 使用 moment 库进行本地化格式化
        // 确保时间戳是可被 moment 解析的，例如 ISO 8601 格式
        // 如果后端返回的时间戳是 UNIX 时间戳（秒或毫秒），需要相应调整
        return moment(timestamp).format('YYYY-MM-DD HH:mm:ss');
      }
      return 'N/A';
    },
    getActionText(action) {
      const actions = {
        'blacklisted': '已拉黑',
        'query_failed': '查询失败',
        'processing_failed': '处理失败',
        'reversal': '解除拉黑' 
      };
      return actions[action] || action; 
    },
    getActionClass(action) {
      switch (action) {
        case 'blacklisted':
          return 'action-blacklisted';
        case 'query_failed':
        case 'processing_failed':
          return 'action-failed';
        case 'reversal':
          return 'action-reversal';
        default:
          return '';
      }
    }
  }
}
</script>

<style scoped>
/* 核心容器样式保持不变 */
.monitor-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  /* 使用父组件定义的CSS变量来统一高度 */
  height: var(--fixed-card-height); /* 将max-height改为height以强制高度一致 */
}

.monitor-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.card-header {
  padding: 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.1);
  flex-shrink: 0; /* 防止 header 被压缩 */
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.card-icon {
  font-size: 1.2rem;
  color: #f7b924; /* 警告或注意的颜色 */
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #e53e3e; /* 默认红色，表示无日志或未启用 */
  transition: all 0.3s ease;
}

.status-indicator.active {
  background: #38a169; /* 有日志时变为绿色 */
  box-shadow: 0 0 8px rgba(56, 161, 105, 0.5);
}

.card-content {
  flex: 1; /* 填充剩余空间 */
  /* overflow-y: auto; 这条在这里可以移除，因为滚动由 .log-scroll-area 控制 */
  padding: 1rem;
  color: rgba(255, 255, 255, 0.8);
  display: flex; /* 让内部的 .log-list 能够使用 flex */
  flex-direction: column; /* 确保内容是垂直布局 */
  min-height: 0; /* 允许 flex item 缩小 */
}

/* 日志列表样式 */
.log-list {
  display: flex;
  flex-direction: column;
  flex: 1; /* 填充父容器高度 */
  min-height: 0; /* 允许 flex item 缩小 */
}

.log-item {
  display: flex;
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 0.85rem;
}

.log-item.header {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  background: rgba(0, 0, 0, 0.1);
  position: sticky; /* 表头固定 */
  top: 0;
  z-index: 1;
  flex-shrink: 0; /* 确保表头不被压缩 */
}

.log-item:last-child {
  border-bottom: none;
}

.log-col {
  flex: 1; 
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0 0.25rem;
}

/* 特定列的宽度分配 */
.log-col.ip {
  flex: 1.5; 
  min-width: 100px;
}
.log-col.action {
  flex: 0.8; 
  min-width: 60px;
}
.log-col.reason {
  flex: 2; 
  min-width: 120px;
}
.log-col.score {
  flex: 0.6; 
  min-width: 50px;
  text-align: center;
}
.log-col.time {
  flex: 1.5; 
  min-width: 120px;
  text-align: right;
}

/* 特定操作的颜色 */
.action-blacklisted {
  color: #e53e3e; 
  font-weight: 700;
}
.action-failed {
  color: #f6ad55; 
}
.action-reversal {
  color: #4299e1; 
}

.no-logs {
  padding: 2rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
  flex-grow: 1; /* 让无日志提示也能够撑开空间 */
  display: flex;
  align-items: center;
  justify-content: center;
}

.log-scroll-area {
  flex: 1; /* 允许滚动区域填充可用空间 */
  overflow-y: auto; /* 关键：使内容可滚动 */
  min-height: 0; /* 允许 flex item 缩小 */
}

/* 滚动条美化 (可选) */
.log-scroll-area::-webkit-scrollbar {
  width: 8px;
}
.log-scroll-area::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}
.log-scroll-area::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}
.log-scroll-area::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.3);
}
</style>