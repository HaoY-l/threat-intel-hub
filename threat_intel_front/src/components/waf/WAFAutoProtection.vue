<template>
  <div class="monitor-card auto-protection">
    <div class="card-header">
      <div class="card-title">
        <i class="card-icon fa fa-bolt"></i>
        <span>自动封禁日志</span>
        <span class="time-range">{{ getDisplayTimeRange(threatTimeRange) }}</span>
      </div>
      <div class="card-actions">
        <select :value="threatTimeRange" @change="$emit('update:threatTimeRange', $event.target.value); fetchProtectedIpLogs()" class="time-selector">
          <option value="today">今天</option>
          <option value="3d">3天</option>
          <option value="7d">7天</option>
          <option value="1m">1个月</option>
        </select>
        <button @click="fetchProtectedIpLogs" class="mini-refresh">
          <i class="fa fa-refresh"></i>
        </button>
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
            <div class="log-col action" :class="getActionClass(log.action)" :title="getActionText(log.action)">
              {{ getActionText(log.action) }}
            </div>
            <div class="log-col reason" :title="log.reason || '无'">{{ log.reason || '无' }}</div>
            <div class="log-col score" :title="log.reputation_score !== null ? log.reputation_score.toString() : 'N/A'">
              {{ log.reputation_score !== null ? log.reputation_score : 'N/A' }}
            </div>
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
  props: {
    threatTimeRange: {
      type: String,
      default: 'today'
    }
  },
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
        const response = await axios.get('/api/protected_ip', {
          params: { range: this.threatTimeRange }
        });
        this.logs = response.data;
      } catch (error) {
        console.error('获取自动封禁日志失败:', error);
        this.logs = [];
      }
    },
    formatTime(timestamp) {
      if (timestamp) {
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
        case 'blacklisted': return 'action-blacklisted';
        case 'query_failed':
        case 'processing_failed': return 'action-failed';
        case 'reversal': return 'action-reversal';
        default: return '';
      }
    },
    getDisplayTimeRange(rangeType) {
      switch (rangeType) {
        case 'today': return '(今天)';
        case '3d': return '(3天内)';
        case '7d': return '(7天内)';
        case '1m': return '(1个月内)';
        default: return '';
      }
    }
  }
}
</script>

<style scoped>
/* 样式保持原有，增加时间选择器和刷新按钮样式 */
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
  height: var(--fixed-card-height);
}
.monitor-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.card-header {
  padding: 0.7rem 0.9rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 600;
  font-size: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #E0E0E0;
}

.card-icon {
  color: #d896ff;
  font-size: 1.2rem;
}

.time-range {
  font-size: 0.85rem;
  color: #B0B0B0;
  margin-left: 0.25rem;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.time-selector {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #E0E0E0;
  font-size: 0.8rem;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  outline: none;
}
.time-selector:hover {
  background: rgba(255, 255, 255, 0.2);
}

.mini-refresh {
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 0.9rem;
  transition: color 0.2s ease;
}
.mini-refresh:hover {
  color: #E0E0E0;
}
.mini-refresh i {
  animation: spin 2s linear infinite;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #f44336;
  transition: background-color 0.3s ease;
}
.status-indicator.active {
  background-color: #4CAF50;
}

.card-content {
  flex-grow: 1;
  overflow: hidden;
  padding: 0.5rem 0.9rem 0.9rem 0.9rem;
  display: flex;
  flex-direction: column;
}

/* 日志列表样式 */
.log-list {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.log-scroll-area {
  flex-grow: 1;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) rgba(255, 255, 255, 0.1);
}
.log-scroll-area::-webkit-scrollbar {
  width: 8px;
}
.log-scroll-area::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
.log-scroll-area::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  border: 2px solid transparent;
  background-clip: padding-box;
}

.log-item {
  display: grid;
  grid-template-columns: 1.5fr 0.8fr 1.5fr 0.5fr 1.5fr;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 0.85rem;
  color: #E0E0E0;
  transition: background-color 0.2s ease;
}

.log-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.log-item.header {
  font-weight: bold;
  color: #B0B0B0;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
  position: sticky;
  top: 0;
  background: rgba(0, 0, 0, 0.2);
  z-index: 10;
}

.log-col {
  padding-right: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.log-col.ip {
  color: #72B1FF;
}

.log-col.action {
  font-weight: 500;
}
.action-blacklisted {
  color: #ff7272;
}
.action-reversal {
  color: #8aff8a;
}
.action-failed {
  color: #FFB347;
}

.log-col.score {
  color: #FFC107;
}

.log-col.time {
  color: #B0B0B0;
  font-size: 0.8rem;
}

.no-logs {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #aaa;
  font-size: 0.9rem;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>