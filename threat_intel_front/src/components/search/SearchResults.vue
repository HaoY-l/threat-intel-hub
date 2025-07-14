<template>
  <div class="search-results">
    <h3 class="results-header">查询结果</h3>
    
    <div class="results-list">
      <div 
        v-for="(result, index) in results" 
        :key="index"
        class="result-item"
      >
        <div class="result-header">
          <div class="result-info">
            <code class="result-id">{{ result.id }}</code>
            <span class="threat-level" :class="getThreatClass(result.threat_level)">
              {{ result.threat_level }}
            </span>
          </div>
          <div class="score-section">
            <div class="score-label">风险评分</div>
            <div class="score-value">{{ result.reputation_score }}</div>
          </div>
        </div>
        
        <div class="result-details">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="label">数据源:</span>
              <span class="value">{{ result.source }}</span>
            </div>
            <div class="detail-item">
              <span class="label">更新时间:</span>
              <span class="value">{{ formatDate(result.last_update) }}</span>
            </div>
          </div>
          
          <div v-if="result.details" class="raw-details">
            <div class="details-label">详细信息:</div>
            <pre class="details-content">{{ formatDetails(result.details) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchResults',
  props: {
    results: {
      type: Array,
      default: () => []
    },
    searchType: {
      type: String,
      default: 'ip'
    }
  },
  methods: {
    getThreatClass(level) {
      const levelMap = {
        'malicious': 'threat-malicious',
        'suspicious': 'threat-suspicious',
        'harmless': 'threat-harmless'
      }
      return levelMap[level] || 'threat-unknown'
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleString('zh-CN')
    },
    
    formatDetails(details) {
      return JSON.stringify(details, null, 2)
    }
  }
}
</script>

<style scoped>
.search-results {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 1rem;
  padding: 1.5rem;
}

.results-header {
  font-size: 1.125rem;
  font-weight: 500;
  color: white;
  margin: 0 0 1rem 0;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.result-item {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(71, 85, 105, 0.5);
  border-radius: 0.5rem;
  padding: 1rem;
}

.result-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.result-id {
  color: #06b6d4;
  font-family: 'Courier New', monospace;
  font-weight: 600;
}

.threat-level {
  font-weight: 500;
  text-transform: uppercase;
  font-size: 0.875rem;
}

.threat-malicious {
  color: #ef4444;
}

.threat-suspicious {
  color: #f97316;
}

.threat-harmless {
  color: #22c55e;
}

.threat-unknown {
  color: #6b7280;
}

.score-section {
  text-align: right;
}

.score-label {
  font-size: 0.875rem;
  color: #a855f7;
  margin-bottom: 0.25rem;
}

.score-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.detail-item {
  font-size: 0.875rem;
}

.label {
  color: #9ca3af;
  margin-right: 0.5rem;
}

.value {
  color: white;
}

.raw-details {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.375rem;
}

.details-label {
  color: #9ca3af;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.details-content {
  color: #a855f7;
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

@media (max-width: 640px) {
  .result-header {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
}
</style>