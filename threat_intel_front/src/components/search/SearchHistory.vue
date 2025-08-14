<template>
  <div class="search-history">
    <h3 class="history-header">
      <i class="fas fa-clock"></i>
      查询历史
    </h3>
    
    <div class="history-list">
      <div 
        v-for="item in history" 
        :key="item.id"
        class="history-item"
        :class="{ 'expanded': item.expanded }"
      >
        <!-- 历史记录简要信息 -->
        <div class="history-content" @click="toggleHistoryDetails(item)">
          <div class="history-info">
            <i :class="getTypeIcon(item.type)"></i>
            <code class="history-query" :title="item.query">{{ item.query }}</code>
            <span class="result-count">{{ item.results || 0 }} 结果</span>
            <span 
              v-if="item.maxThreatLevel"
              class="threat-level"
              :class="getThreatLevelClass(item.maxThreatLevel)"
            >
              {{ getThreatLevelText(item.maxThreatLevel) }}
            </span>
            <span 
              v-if="item.maxScore !== undefined"
              class="max-score"
              :class="getScoreClass(item.maxScore)"
            >
              风险: {{ item.maxScore }}
            </span>
          </div>
          <div class="history-actions">
            <span class="history-time">{{ formatTime(item.timestamp) }}</span>
            <button 
              class="action-btn search-again-btn"
              @click.stop="handleSearchAgain(item)"
              title="重新查询"
            >
              <i class="fas fa-redo"></i>
            </button>
            <button 
              class="action-btn expand-btn"
              @click.stop="toggleHistoryDetails(item)"
              title="查看详情"
            >
              <i class="fas fa-chevron-down" :class="{ 'rotated': item.expanded }"></i>
            </button>
          </div>
        </div>
        
        <!-- 详细结果展示 -->
        <div v-if="item.expanded && item.detailResults" class="history-details">
          <div class="details-header">
            <span class="details-title">
              <i class="fas fa-list"></i>
              详细查询结果
            </span>
            <div class="details-stats">
              <span class="stat-item">
                <i class="fas fa-database"></i>
                {{ getUniqueSourcesCount(item.detailResults) }} 个数据源
              </span>
              <span class="stat-item">
                <i class="fas fa-shield-alt"></i>
                平均分: {{ getAverageScore(item.detailResults) }}
              </span>
            </div>
          </div>
          
          <div class="results-container">
            <div 
              v-for="(result, index) in item.detailResults" 
              :key="index"
              class="result-item"
            >
              <!-- 结果头部信息 -->
              <div class="result-header">
                <div class="result-info">
                  <i :class="getTypeIcon(item.type)"></i>
                  <code 
                    class="result-id" 
                    :title="getDisplayId(result, item.type)"
                  >
                    {{ getDisplayId(result, item.type) }}
                  </code>
                  <span 
                    class="threat-badge" 
                    :class="getThreatLevelClass(result.threat_level)"
                  >
                    <i :class="getThreatIcon(result.threat_level)"></i>
                    {{ getThreatLevelText(result.threat_level) }}
                  </span>
                </div>
                <div class="score-section">
                  <div class="score-label">风险评分</div>
                  <div 
                    class="score-value" 
                    :class="getScoreClass(result.reputation_score)"
                  >
                    {{ result.reputation_score || 0 }}
                  </div>
                </div>
              </div>
              
              <!-- 结果详细信息 -->
              <div class="result-details">
                <div class="detail-grid">
                  <div class="detail-item">
                    <i class="fas fa-database"></i>
                    <span class="label">数据源:</span>
                    <span class="value">{{ result.source || '未知' }}</span>
                  </div>
                  <div class="detail-item">
                    <i class="fas fa-clock"></i>
                    <span class="label">更新时间:</span>
                    <span class="value">{{ formatDate(result.last_update) }}</span>
                  </div>
                  <div v-if="item.type === 'url'" class="detail-item">
                    <i class="fas fa-link"></i>
                    <span class="label">目标URL:</span>
                    <span class="value url-value" :title="result.target_url">{{ result.target_url || result.id }}</span>
                  </div>
                  <div v-if="item.type === 'file'" class="detail-item">
                    <i class="fas fa-fingerprint"></i>
                    <span class="label">文件哈希:</span>
                    <span class="value hash-value" :title="result.id">{{ result.id }}</span>
                  </div>
                </div>
                
                <!-- 原始数据展开 -->
                <div class="details-toggle">
                  <button 
                    @click="toggleRawDetails(item.id, index)"
                    class="toggle-btn"
                    :class="{ active: isRawDetailsExpanded(item.id, index) }"
                  >
                    <i class="fas fa-chevron-down"></i>
                    <span>{{ isRawDetailsExpanded(item.id, index) ? '收起' : '展开' }}原始数据</span>
                  </button>
                </div>
                
                <div 
                  v-if="isRawDetailsExpanded(item.id, index) && result.details" 
                  class="raw-details"
                >
                  <div class="details-label">
                    <i class="fas fa-code"></i>
                    原始数据:
                  </div>
                  <div class="details-content-wrapper">
                    <pre class="details-content">{{ formatDetails(result.details) }}</pre>
                    <button 
                      @click="copyDetails(result.details)"
                      class="copy-btn"
                      title="复制详细信息"
                    >
                      <i class="fas fa-copy"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchHistory',
  props: {
    history: {
      type: Array,
      default: () => []
    }
  },
  emits: ['search-again'],
  data() {
    return {
      expandedRawDetails: new Set()
    }
  },
  methods: {
    getTypeIcon(type) {
      const iconMap = {
        'ip': 'fas fa-server',
        'url': 'fas fa-globe',
        'file': 'fas fa-file'
      }
      return iconMap[type] || 'fas fa-search'
    },
    getThreatLevelClass(level) {
      const levelMap = {
        'malicious': 'threat-malicious',
        'suspicious': 'threat-suspicious',
        'harmless': 'threat-harmless',
        'clean': 'threat-harmless'
      }
      return levelMap[level] || 'threat-unknown'
    },
    getThreatIcon(level) {
      const iconMap = {
        'malicious': 'fas fa-skull-crossbones',
        'suspicious': 'fas fa-exclamation-triangle',
        'harmless': 'fas fa-shield-alt',
        'clean': 'fas fa-shield-alt'
      }
      return iconMap[level] || 'fas fa-question-circle'
    },
    getThreatLevelText(level) {
      const labelMap = {
        'malicious': '恶意',
        'suspicious': '可疑',
        'harmless': '无害',
        'clean': '清洁'
      }
      return labelMap[level] || '未知'
    },
    getScoreClass(score) {
      const numScore = parseInt(score) || 0
      if (numScore < 0) return 'score-high'
      if (numScore === 0) return 'score-medium'
      return 'score-low'
    },
    getDisplayId(result, type) {
      if (type === 'url') {
        return result.target_url || result.id
      }
      return result.id
    },
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN')
    },
    formatDate(dateString) {
      if (!dateString) return '未知'
      try {
        return new Date(dateString).toLocaleString('zh-CN')
      } catch {
        return '格式错误'
      }
    },
    formatDetails(details) {
      if (!details) return ''
      try {
        return JSON.stringify(details, null, 2)
      } catch {
        return String(details)
      }
    },
    toggleHistoryDetails(item) {
      if (!('expanded' in item)) item.expanded = false
      item.expanded = !item.expanded
    },
    toggleRawDetails(historyId, resultIndex) {
      const key = `${historyId}_${resultIndex}`
      if (this.expandedRawDetails.has(key)) {
        this.expandedRawDetails.delete(key)
      } else {
        this.expandedRawDetails.add(key)
      }
    },
    isRawDetailsExpanded(historyId, resultIndex) {
      return this.expandedRawDetails.has(`${historyId}_${resultIndex}`)
    },
    handleSearchAgain(item) {
      this.$emit('search-again', {
        query: item.query,
        type: item.type
      })
    },
    getUniqueSourcesCount(results) {
      const sources = new Set(results.map(r => r.source))
      return sources.size
    },
    getAverageScore(results) {
      if (!results || results.length === 0) return 0
      const total = results.reduce((sum, r) => sum + (r.reputation_score || 0), 0)
      return Math.round(total / results.length)
    },
    async copyDetails(details) {
      try {
        await navigator.clipboard.writeText(JSON.stringify(details, null, 2))
        this.$emit('copy-success')
      } catch (err) {
        console.error('复制失败:', err)
      }
    }
  }
}
</script>

<style scoped>
.search-history {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 1rem;
  padding: 1.5rem;
}

.history-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.125rem;
  font-weight: 500;
  color: white;
  margin: 0 0 1rem 0;
}

.history-header i {
  color: #8b5cf6;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 24rem;
  overflow-y: auto;
}

.history-item {
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid rgba(71, 85, 105, 0.3);
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.history-item:hover {
  border-color: rgba(139, 92, 246, 0.5);
  background: rgba(30, 41, 59, 0.5);
}

.history-item.expanded {
  border-color: rgba(139, 92, 246, 0.4);
  background: rgba(30, 41, 59, 0.6);
}

.history-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  cursor: pointer;
}

.history-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.history-info i {
  color: #8b5cf6;
  width: 1rem;
}

/* 关键：长文本截断显示 */
.history-query,
.hash-value {
  font-family: 'Courier New', monospace;
  font-size: 0.7rem;
  color: #a855f7;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
  max-width: 100%;
}

.result-count {
  color: #a855f7;
  font-size: 0.75rem;
}

.threat-level, .max-score {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  white-space: nowrap;
}

.threat-malicious { color:#ef4444; background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3);}
.threat-suspicious { color:#f97316; background:rgba(249,115,22,0.1); border:1px solid rgba(249,115,22,0.3);}
.threat-harmless { color:#22c55e; background:rgba(34,197,94,0.1); border:1px solid rgba(34,197,94,0.3);}
.threat-unknown { color:#6b7280; background:rgba(107,114,128,0.1); border:1px solid rgba(107,114,128,0.3);}

.score-high { color:#ef4444; background:rgba(239,68,68,0.1);}
.score-medium { color:#f97316; background:rgba(249,115,22,0.1);}
.score-low { color:#22c55e; background:rgba(34,197,94,0.1);}

/* 以下省略，保留原本样式，确保布局正常 */
.history-actions { display:flex; align-items:center; gap:0.5rem;}
.history-time { color:#9ca3af; font-size:0.75rem; }
.action-btn { background: rgba(71,85,105,0.3); border:1px solid rgba(139,92,246,0.3); border-radius:0.25rem; padding:0.25rem 0.5rem; color:#a855f7; cursor:pointer; font-size:0.75rem; transition:all 0.2s ease;}
.action-btn:hover { background: rgba(139,92,246,0.2); border-color: rgba(139,92,246,0.5);}
.expand-btn i.rotated { transform: rotate(180deg); }

/* 结果详细信息样式保持不变，略 */
</style>
