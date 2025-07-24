<template>
  <div class="monitor-card blocked-ips">
    <div class="card-header">
      <div class="card-title">
        <i class="card-icon fa fa-shield"></i>
        <span>规则封禁IP监控</span>
        <span class="time-range">{{ getDisplayTimeRange(blockedTimeRange) }}</span>
      </div>
      <div class="card-actions">
        <select :value="blockedTimeRange" @change="$emit('update:blockedTimeRange', $event.target.value); $emit('fetchBlockedIPs')" class="time-selector">
          <option value="today">今天</option>
          <option value="3d">3天</option>
          <option value="7d">7天</option>
          <option value="1m">1个月</option>
        </select>
        <button @click="$emit('fetchBlockedIPs')" class="mini-refresh">
          <i class="fa fa-refresh"></i>
        </button>
      </div>
    </div>
    <div class="card-content">
      <div class="scrollable-list" v-if="blockedIPs.length > 0">
        <div v-for="(item, index) in blockedIPs" :key="item.ip" class="ip-item blocked-item">
          <div class="ip-main">
            <code class="ip-address">{{ item.ip }}</code>
            <span :class="['threat-badge', getThreatLevelClass(item.threat_level)]">
              {{ item.attack_type || '未知类型' }}
            </span>
          </div>
          <div class="ip-details">
            <span class="detail-time">
              <i class="fa fa-clock-o mr-1"></i>{{ formatTime(item.created_at) }}
            </span>
          </div>
          <div class="ip-actions">
            <button @click="$emit('addToBlacklist', item.ip)" class="action-btn primary action-btn-sm">
              <i class="fa fa-ban mr-1"></i>拉黑
            </button>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <div class="empty-icon"><i class="fa fa-shield"></i></div>
        <p>暂无规则封禁IP记录</p>
      </div>
    </div>
  </div>

  <div class="monitor-card high-freq-ips">
    <div class="card-header">
      <div class="card-title">
        <i class="card-icon fa fa-line-chart"></i>
        <span>高频请求监控</span>
        <span class="time-range">{{ getDisplayTimeRange(freqTimeRange) }}</span>
      </div>
      <div class="card-actions">
        <select :value="freqTimeRange" @change="$emit('update:freqTimeRange', $event.target.value); $emit('fetchHighFreqIPs')" class="time-selector">
          <option value="today">今天</option>
          <option value="3d">3天</option>
          <option value="7d">7天</option>
          <option value="1m">1个月</option>
        </select>
        <button @click="$emit('fetchHighFreqIPs')" class="mini-refresh">
          <i class="fa fa-refresh"></i>
        </button>
      </div>
    </div>
    <div class="card-content">
      <div class="scrollable-list" v-if="highFreqIPs.length > 0">
        <div v-for="(item, index) in highFreqIPs" :key="item.ip" class="ip-item freq-item">
          <div class="ip-main">
            <code class="ip-address">{{ item.ip }}</code>
            <div class="freq-count">{{ item.request_count }} 次</div>
          </div>
          <div class="ip-details">
            <span class="detail-time">
              <i class="fa fa-clock-o mr-1"></i>{{ formatTime(item.created_at) }}
            </span>
          </div>
          <div class="ip-actions">
            <button @click="$emit('blockIP', item.ip)" class="action-btn danger action-btn-sm">
              <i class="fa fa-ban mr-1"></i>封禁IP
            </button>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <div class="empty-icon"><i class="fa fa-line-chart"></i></div>
        <p>暂无高频请求记录</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WAFMonitoringPanel',
  props: {
    blockedIPs: {
      type: Array,
      default: () => []
    },
    blockedTimeRange: {
      type: String,
      default: 'today'
    },
    highFreqIPs: {
      type: Array,
      default: () => []
    },
    freqTimeRange: {
      type: String,
      default: 'today'
    }
  },
  emits: [
    'update:blockedTimeRange',
    'fetchBlockedIPs',
    'update:freqTimeRange',
    'fetchHighFreqIPs',
    'addToBlacklist',
    'blockIP'
  ],
  methods: {
    parseDate(timestamp) {
      if (!timestamp) return null;

      let date;
      if (typeof timestamp === 'string') {
        const gmtRegex = /^(Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s(\d{2})\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s(\d{4})\s(\d{2}):(\d{2}):(\d{2})\sGMT$/;
        const isoRegex = /^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})$/;

        let match = timestamp.match(gmtRegex);
        if (match) {
          const [, dayOfWeek, day, monthStr, year, hour, minute, second] = match;
          const monthIndex = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].indexOf(monthStr);
          date = new Date(Date.UTC(year, monthIndex, day, hour, minute, second));
        } else {
          match = timestamp.match(isoRegex);
          if (match) {
             date = new Date(`${match[1]}T${match[2]}`);
          } else {
             date = new Date(timestamp);
             if (isNaN(date.getTime())) {
                 const cleanedTimestamp = timestamp.replace(' ', 'T');
                 date = new Date(cleanedTimestamp);
             }
          }
        }
      } else {
        date = new Date(timestamp);
      }

      if (isNaN(date.getTime())) {
          console.warn("无法解析的时间戳:", timestamp);
          return null;
      }
      return date;
    },

    // Combined format for single line time display
    formatTime(timestamp) {
      const date = this.parseDate(timestamp);
      if (!date) return '-';
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
    },

    getThreatLevelClass(level) {
      switch (level) {
        case 'high': return 'bg-red-500'
        case 'medium': return 'bg-orange-500'
        case 'low': return 'bg-green-500'
        case 'unknown': return 'bg-gray-500'
        default: return 'bg-gray-500'
      }
    },

    getThreatLevelText(level) {
      switch (level) {
        case 'high': return '高风险'
        case 'medium': return '中风险'
        case 'low': return '低风险'
        case 'unknown': return '未知风险'
        default: return '未知'
      }
    },

    getRiskLevelClass(count) {
      if (count >= 1000) return 'risk-high'
      if (count >= 500) return 'risk-medium'
      return 'risk-low'
    },

    getRiskLevelText(count) {
      if (count >= 1000) return '极高频率'
      if (count >= 500) return '高频率'
      return '中频率'
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
/* Common Styles */
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
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 600;
  font-size: 1rem;
  white-space: nowrap;
}

.card-icon {
  font-size: 1.1rem;
}

.time-range {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  margin-left: 0.3rem;
  white-space: nowrap;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.time-selector {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 5px;
  color: white;
  padding: 0.2rem 0.5rem;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.3rem center;
  background-size: 0.7em;
}

.time-selector:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

.mini-refresh {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.mini-refresh:hover {
  color: #667eea;
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(30deg);
}

/* Card Content - Scrollable List */
.card-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.7rem 0.9rem;
}

.scrollable-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

/* IP Item - 重新设计布局，使用Grid实现均匀分布 */
.ip-item {
  display: grid;
  grid-template-columns: 2.5fr 1.2fr 1fr;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 0.6rem 0.8rem;
  font-size: 0.8rem;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.05);
  min-height: 50px;
}

.ip-item:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.ip-main {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  min-width: 0;
}

.ip-address {
  font-family: 'Cascadia Code', 'Fira Code', monospace;
  background: rgba(0, 0, 0, 0.25);
  padding: 3px 8px;
  border-radius: 5px;
  color: #a0f0ed;
  user-select: text;
  white-space: nowrap;
  font-size: 0.85rem;
  line-height: 1.2;
  flex-shrink: 0;
  min-width: 120px; /* 确保IP地址有足够的显示空间 */
}

.threat-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-weight: 600;
  color: white;
  user-select: none;
  white-space: nowrap;
  font-size: 0.7rem;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.bg-red-500 { background-color: #e53e3e; }
.bg-orange-500 { background-color: #ed8936; }
.bg-green-500 { background-color: #38a169; }
.bg-gray-500 { background-color: #718096; }

/* High frequency count styling - 移除风险指示器 */
.freq-count {
  background: rgba(66, 153, 225, 0.25);
  color: #4299e1;
  border-radius: 12px;
  padding: 0.2rem 0.6rem;
  font-weight: 600;
  user-select: none;
  white-space: nowrap;
  font-size: 0.7rem;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* IP Details - 调整为单行显示 */
.ip-details {
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.75rem;
  white-space: nowrap;
}

.detail-time {
  display: flex;
  align-items: center;
}

.mr-1 {
  margin-right: 0.2rem;
}

/* IP Action Buttons */
.ip-actions {
  display: flex;
  justify-content: flex-end;
}

.action-btn {
  padding: 0.2rem 0.5rem;
  border: none;
  border-radius: 5px;
  font-size: 0.7rem;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  line-height: 1;
  white-space: nowrap;
}

.action-btn.primary { 
  background-color: #4299e1; 
  color: white; 
}

.action-btn.primary:hover { 
  background-color: #3182ce; 
  transform: translateY(-1px); 
  box-shadow: 0 2px 6px rgba(66, 153, 225, 0.2); 
}

.action-btn.danger { 
  background-color: #e53e3e; 
  color: white; 
}

.action-btn.danger:hover { 
  background-color: #c53030; 
  transform: translateY(-1px); 
  box-shadow: 0 2px 6px rgba(229, 62, 62, 0.2); 
}

/* Empty State */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.95rem;
  user-select: none;
  padding: 1.8rem 0;
}

.empty-icon {
  font-size: 2.6rem;
  margin-bottom: 0.5rem;
  color: rgba(255, 255, 255, 0.3);
}

/* Responsive Adjustments */
@media (max-width: 1200px) {
  .ip-item {
    grid-template-columns: 2.2fr 1fr 1fr;
    gap: 0.8rem;
    padding: 0.5rem 0.7rem;
  }
  
  .ip-address {
    font-size: 0.8rem;
    min-width: 110px;
  }
  
  .threat-badge, .freq-count {
    font-size: 0.65rem;
    padding: 0.15rem 0.5rem;
  }
  
  .ip-details {
    font-size: 0.7rem;
  }
  
  .action-btn {
    font-size: 0.65rem;
    padding: 0.15rem 0.4rem;
  }
}

@media (max-width: 992px) {
  .ip-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    text-align: center;
    padding: 0.6rem;
  }

  .ip-main {
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .ip-address {
    min-width: unset;
    font-size: 0.85rem;
  }

  .ip-details {
    justify-content: center;
    font-size: 0.75rem;
  }

  .ip-actions {
    justify-content: center;
  }

  .action-btn {
    font-size: 0.75rem;
    padding: 0.25rem 0.6rem;
  }
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.4rem;
  }
  
  .card-actions {
    width: 100%;
    justify-content: space-between;
    margin-top: 0.2rem;
  }
  
  .time-selector, .mini-refresh {
    font-size: 0.8rem;
    padding: 0.3rem 0.6rem;
    height: auto;
    width: auto;
  }
  
  .mini-refresh { 
    width: 32px; 
    height: 32px; 
  }
  
  .card-title {
    font-size: 0.95rem;
  }
  
  .card-icon {
    font-size: 1.1rem;
  }
  
  .time-range {
    margin-left: 0;
  }
  
  .empty-state p {
    font-size: 0.9rem;
  }
  
  .empty-icon {
    font-size: 2.4rem;
  }
}

@media (max-width: 480px) {
  .card-title {
    font-size: 0.9rem;
  }
  
  .card-icon {
    font-size: 1rem;
  }
  
  .time-selector {
    font-size: 0.7rem;
    padding: 0.15rem 0.3rem;
  }
  
  .mini-refresh {
    width: 28px; 
    height: 28px;
    font-size: 1rem;
  }
  
  .ip-item {
    padding: 0.5rem;
  }
  
  .ip-address {
    font-size: 0.75rem;
  }
  
  .threat-badge, .freq-count {
    font-size: 0.65rem;
    padding: 0.1rem 0.4rem;
  }
  
  .ip-details {
    font-size: 0.65rem;
  }
  
  .action-btn {
    font-size: 0.65rem;
    padding: 0.15rem 0.4rem;
  }
}
</style>