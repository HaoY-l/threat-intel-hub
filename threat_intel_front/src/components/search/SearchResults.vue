<template>
  <div v-if="visible" class="dialog-overlay" @click="closeDialog">
    <div class="dialog-container" @click.stop>
      <!-- 弹框头部 -->
      <div class="dialog-header">
        <div class="header-left">
          <i class="fas fa-shield-alt"></i>
          <h3>威胁情报查询结果</h3>
        </div>
        <div class="header-right">
          <span class="target-info">{{ queryValue }}</span>
          <button @click="closeDialog" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>

      <!-- 弹框内容 -->
      <div class="dialog-content">
        <div class="search-results">
          <div class="results-header">
            <span class="results-count">
              共 {{ Object.keys(threatData.results || {}).length }} 个数据源
            </span>
            <div class="overall-status" :class="getOverallThreatClass()">
              <i :class="getOverallThreatIcon()"></i>
              {{ getOverallThreatLabel() }}
            </div>
          </div>
          
          <div class="results-list">
            <div 
              v-for="(result, source) in threatData.results" 
              :key="source"
              class="result-item"
            >
              <div class="result-header">
                <div class="result-info">
                  <i :class="getTypeIcon(threatData.type)"></i>
                  <span class="source-name">{{ source }}</span>
                  <span 
                    class="threat-level" 
                    :class="getThreatClass(result.threat_level)"
                  >
                    <i :class="getThreatIcon(result.threat_level)"></i>
                    {{ getThreatLabel(result.threat_level) }}
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
              
              <div class="result-details">
                <div class="detail-grid">
                  <div class="detail-item">
                    <i class="fas fa-database"></i>
                    <span class="label">数据源:</span>
                    <span class="value">{{ result.source || source }}</span>
                  </div>
                  <div class="detail-item">
                    <i class="fas fa-clock"></i>
                    <span class="label">最后更新:</span>
                    <span class="value">{{ formatDate(result.last_update) }}</span>
                  </div>
                  <div class="detail-item">
                    <i class="fas fa-history"></i>
                    <span class="label">创建时间:</span>
                    <span class="value">{{ formatDate(result.created_at) }}</span>
                  </div>
                  <div class="detail-item">
                    <i class="fas fa-memory"></i>
                    <span class="label">缓存状态:</span>
                    <span class="value cache-status" :class="{ cached: result.from_cache }">
                      {{ result.from_cache ? '缓存' : '实时' }}
                    </span>
                  </div>
                </div>
                
                <!-- 详细信息展开 -->
                <div class="details-toggle">
                  <button 
                    @click="toggleDetails(source)"
                    class="toggle-btn"
                    :class="{ active: expandedItems.includes(source) }"
                  >
                    <i class="fas fa-chevron-down"></i>
                    <span>{{ expandedItems.includes(source) ? '收起' : '展开' }}详细信息</span>
                  </button>
                </div>
                
                <div 
                  v-if="expandedItems.includes(source) && result.details" 
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

      <!-- 弹框底部操作 -->
      <div class="dialog-footer">
        <button @click="exportResults" class="export-btn">
          <i class="fas fa-download"></i>
          导出结果
        </button>
        <button @click="closeDialog" class="close-btn-secondary">
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ThreatIntelDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    threatData: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      expandedItems: []
    }
  },
  computed: {
    queryValue() {
      return this.threatData.value || '未知'
    }
  },
  methods: {
    closeDialog() {
      this.$emit('close')
    },
    
    getOverallThreatClass() {
      const results = this.threatData.results || {}
      const threatLevels = Object.values(results).map(r => r.threat_level)
      
      if (threatLevels.includes('high') || threatLevels.includes('malicious')) {
        return 'threat-malicious'
      }
      if (threatLevels.includes('medium') || threatLevels.includes('suspicious')) {
        return 'threat-suspicious'
      }
      if (threatLevels.includes('low') || threatLevels.includes('harmless')) {
        return 'threat-harmless'
      }
      return 'threat-unknown'
    },
    
    getOverallThreatIcon() {
      const overallClass = this.getOverallThreatClass()
      const iconMap = {
        'threat-malicious': 'fas fa-skull-crossbones',
        'threat-suspicious': 'fas fa-exclamation-triangle',
        'threat-harmless': 'fas fa-shield-alt',
        'threat-unknown': 'fas fa-question-circle'
      }
      return iconMap[overallClass] || 'fas fa-question-circle'
    },
    
    getOverallThreatLabel() {
      const overallClass = this.getOverallThreatClass()
      const labelMap = {
        'threat-malicious': '高风险',
        'threat-suspicious': '中风险',
        'threat-harmless': '低风险',
        'threat-unknown': '未知风险'
      }
      return labelMap[overallClass] || '未知风险'
    },
    
    getTypeIcon(type) {
      const iconMap = {
        'ip': 'fas fa-server',
        'url': 'fas fa-globe',
        'file': 'fas fa-file',
        'domain': 'fas fa-link'
      }
      return iconMap[type] || 'fas fa-search'
    },
    
    getThreatClass(level) {
      const levelMap = {
        'high': 'threat-malicious',
        'malicious': 'threat-malicious',
        'medium': 'threat-suspicious',
        'suspicious': 'threat-suspicious',
        'low': 'threat-harmless',
        'harmless': 'threat-harmless',
        'clean': 'threat-harmless'
      }
      return levelMap[level] || 'threat-unknown'
    },
    
    getThreatIcon(level) {
      const iconMap = {
        'high': 'fas fa-skull-crossbones',
        'malicious': 'fas fa-skull-crossbones',
        'medium': 'fas fa-exclamation-triangle',
        'suspicious': 'fas fa-exclamation-triangle',
        'low': 'fas fa-shield-alt',
        'harmless': 'fas fa-shield-alt',
        'clean': 'fas fa-shield-alt'
      }
      return iconMap[level] || 'fas fa-question-circle'
    },
    
    getThreatLabel(level) {
      const labelMap = {
        'high': '高风险',
        'malicious': '恶意',
        'medium': '中风险',
        'suspicious': '可疑',
        'low': '低风险',
        'harmless': '无害',
        'clean': '清洁'
      }
      return labelMap[level] || '未知'
    },
    
    getScoreClass(score) {
      const numScore = parseInt(score) || 0
      if (numScore > 0) return 'score-low'      // 正数为绿色
      if (numScore === 0) return 'score-low'    // 0 也为绿色
      if (numScore >= -10) return 'score-medium'
      return 'score-high'                       // 负数为红色
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
      if (!details) return '暂无详细信息'
      try {
        return JSON.stringify(details, null, 2)
      } catch {
        return String(details)
      }
    },
    
    toggleDetails(source) {
      const pos = this.expandedItems.indexOf(source)
      if (pos === -1) {
        this.expandedItems.push(source)
      } else {
        this.expandedItems.splice(pos, 1)
      }
    },
    
    async copyDetails(details) {
      try {
        await navigator.clipboard.writeText(JSON.stringify(details, null, 2))
        this.$emit('copy-success')
      } catch (err) {
        console.error('复制失败:', err)
      }
    },
    
    exportResults() {
      const dataStr = JSON.stringify(this.threatData, null, 2)
      const blob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `threat_intel_${this.queryValue}_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
  }
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.dialog-container {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 1rem;
  max-width: 90vw;
  max-height: 85vh;
  width: 1000px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(71, 85, 105, 0.3);
  background: rgba(30, 41, 59, 0.5);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-left i {
  color: #8b5cf6;
  font-size: 1.25rem;
}

.header-left h3 {
  color: white;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.target-info {
  color: #06b6d4;
  font-family: 'Courier New', monospace;
  font-weight: 600;
  font-size: 0.875rem;
  background: rgba(6, 182, 212, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid rgba(6, 182, 212, 0.3);
}

.close-btn {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 0.375rem;
  padding: 0.5rem;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.3);
  border-color: rgba(239, 68, 68, 0.5);
}

.dialog-content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.search-results {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.results-count {
  color: #a855f7;
  font-size: 0.875rem;
  font-weight: 500;
}

.overall-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.875rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  white-space: nowrap;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-item {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(71, 85, 105, 0.5);
  border-radius: 0.75rem;
  padding: 1.25rem;
  transition: all 0.2s ease;
}

.result-item:hover {
  border-color: rgba(139, 92, 246, 0.4);
  background: rgba(30, 41, 59, 0.7);
}

.result-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.result-info > i {
  color: #8b5cf6;
  width: 1.25rem;
  font-size: 1.125rem;
}

.source-name {
  color: white;
  font-weight: 600;
  font-size: 1rem;
}

.threat-level {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 500;
  text-transform: uppercase;
  font-size: 0.875rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  white-space: nowrap;
}

.threat-malicious {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.threat-suspicious {
  color: #f97316;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.3);
}

.threat-harmless {
  color: #22c55e;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.threat-unknown {
  color: #6b7280;
  background: rgba(107, 114, 128, 0.1);
  border: 1px solid rgba(107, 114, 128, 0.3);
}

.score-section {
  text-align: right;
}

.score-label {
  font-size: 0.875rem;
  color: #a855f7;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.score-value {
  font-size: 1.5rem;
  font-weight: 700;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  min-width: 3rem;
  text-align: center;
}

.score-high {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.score-medium {
  color: #f97316;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.3);
}

.score-low {
  color: #22c55e;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.detail-item i {
  color: #8b5cf6;
  width: 1rem;
}

.label {
  color: #9ca3af;
  font-weight: 500;
  white-space: nowrap;
}

.value {
  color: white;
  flex: 1;
}

.cache-status.cached {
  color: #22c55e;
}

.details-toggle {
  display: flex;
  justify-content: center;
  margin-top: 0.5rem;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(71, 85, 105, 0.5);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 0.5rem;
  padding: 0.625rem 1.25rem;
  color: #a855f7;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn:hover {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.5);
}

.toggle-btn.active i {
  transform: rotate(180deg);
}

.raw-details {
  margin-top: 1rem;
  padding: 1.25rem;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(71, 85, 105, 0.3);
  border-radius: 0.75rem;
}

.details-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #9ca3af;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.75rem;
}

.details-content-wrapper {
  position: relative;
}

.details-content {
  color: #a855f7;
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 2rem;
}

.copy-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(139, 92, 246, 0.2);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 0.25rem;
  padding: 0.375rem 0.75rem;
  color: #a855f7;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.copy-btn:hover {
  background: rgba(139, 92, 246, 0.3);
  border-color: rgba(139, 92, 246, 0.5);
}

.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid rgba(71, 85, 105, 0.3);
  background: rgba(30, 41, 59, 0.5);
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(139, 92, 246, 0.2);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 0.5rem;
  padding: 0.625rem 1.25rem;
  color: #a855f7;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.export-btn:hover {
  background: rgba(139, 92, 246, 0.3);
  border-color: rgba(139, 92, 246, 0.5);
}

.close-btn-secondary {
  background: rgba(71, 85, 105, 0.5);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 0.5rem;
  padding: 0.625rem 1.25rem;
  color: #9ca3af;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn-secondary:hover {
  background: rgba(71, 85, 105, 0.7);
  color: white;
}

.details-content::-webkit-scrollbar {
  width: 4px;
}

.details-content::-webkit-scrollbar-track {
  background: rgba(30, 41, 59, 0.5);
  border-radius: 2px;
}

.details-content::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.5);
  border-radius: 2px;
}

.dialog-content::-webkit-scrollbar {
  width: 6px;
}

.dialog-content::-webkit-scrollbar-track {
  background: rgba(30, 41, 59, 0.5);
  border-radius: 3px;
}

.dialog-content::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.5);
  border-radius: 3px;
}

@media (max-width: 768px) {
  .dialog-container {
    width: 95vw;
    max-height: 90vh;
  }
  
  .dialog-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .header-right {
    width: 100%;
    justify-content: space-between;
  }
  
  .result-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .result-info {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .dialog-footer {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .export-btn,
  .close-btn-secondary {
    width: 100%;
    justify-content: center;
  }
}
</style>