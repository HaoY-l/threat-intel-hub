<template>
  <div class="cve-card" @click="$emit('click', cve)">
    <div class="card-header">
      <div class="cve-info">
        <code class="cve-id">{{ cve.cve_id }}</code>
        <span class="severity" :class="getSeverityClass(cve.severity)">
          {{ cve.severity }}
        </span>
      </div>
      <span class="date">{{ formatDate(cve.published) }}</span>
    </div>
    
    <h3 class="title">{{ cve.title }}</h3>
    <p class="description">{{ cve.description }}</p>
    
    <div class="card-footer">
      <span class="source">来源: {{ cve.source }}</span>
      <i class="fas fa-chevron-right"></i>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CVECard',
  props: {
    cve: {
      type: Object,
      required: true
    }
  },
  emits: ['click'],
  methods: {
    getSeverityClass(severity) {
      const severityMap = {
        'CRITICAL': 'severity-critical',
        'HIGH': 'severity-high',
        'MEDIUM': 'severity-medium',
        'LOW': 'severity-low'
      }
      return severityMap[severity] || 'severity-unknown'
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('zh-CN')
    }
  }
}
</script>

<style scoped>
.cve-card {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(71, 85, 105, 0.5);
  border-radius: 0.5rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 120px; /* 固定最小高度，与新闻卡片一致 */
  min-width: 280px;  /* 固定最小宽度，防止被挤压过小 */
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* 确保内容均匀分布 */
}

.cve-card:hover {
  border-color: rgba(139, 92, 246, 0.5);
  transform: translateY(-1px);
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.cve-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.cve-id {
  color: #06b6d4;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  font-weight: 600;
}

.severity {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: white;
}

.severity-critical {
  background: #ef4444;
}

.severity-high {
  background: #f97316;
}

.severity-medium {
  background: #eab308;
}

.severity-low {
  background: #22c55e;
}

.severity-unknown {
  background: #6b7280;
}

.date {
  font-size: 0.75rem;
  color: #a855f7;
}

.title {
  color: white;
  font-size: 1rem;
  font-weight: 500;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1; /* 限制为1行，与新闻卡片一致 */
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.description {
  color: #9ca3af;
  font-size: 0.875rem;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.source {
  font-size: 0.75rem;
  color: #a855f7;
}

.card-footer i {
  color: #8b5cf6;
  font-size: 0.875rem;
}
</style>