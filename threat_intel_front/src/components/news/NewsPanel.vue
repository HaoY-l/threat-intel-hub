<template>
  <div class="news-panel">
    <div class="panel-header">
      <h2 class="panel-title">
        <span class="icon">📰</span>
        安全资讯
        <span class="count">{{ newsData.length }}条</span>
      </h2>
      <div class="refresh-btn" @click="refreshNews">
        <span class="refresh-icon">🔄</span>
      </div>
    </div>

    <div class="news-list">
      <div 
        v-for="news in newsData" 
        :key="news.id"
        class="news-item"
        :class="getSeverityClass(news.severity)"
        @click="openNewsDetail(news)"
      >
        <div class="news-header">
          <span class="category-tag" :class="getCategoryClass(news.category)">
            {{ news.category }}
          </span>
          <span class="severity-badge" :class="getSeverityClass(news.severity)">
            {{ news.severity }}
          </span>
        </div>
        
        <h3 class="news-title">{{ news.title }}</h3>
        <p class="news-summary">{{ news.summary }}</p>
        
        <div class="news-footer">
          <span class="news-source">{{ news.source }}</span>
          <span class="news-time">{{ news.time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NewsPanel',
  props: {
    newsData: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    getSeverityClass(severity) {
      const classes = {
        '严重': 'severity-critical',
        '高危': 'severity-high', 
        '中危': 'severity-medium',
        '低危': 'severity-low'
      }
      return classes[severity] || 'severity-unknown'
    },

    getCategoryClass(category) {
      const classes = {
        'APT攻击': 'category-apt',
        '数据泄露': 'category-breach',
        '恶意软件': 'category-malware',
        '工控安全': 'category-ics',
        '钓鱼攻击': 'category-phishing'
      }
      return classes[category] || 'category-default'
    },

    openNewsDetail(news) {
      // 这里可以实现新闻详情弹窗或跳转
      console.log('打开新闻详情:', news)
    },

    refreshNews() {
      this.$emit('refresh')
    }
  }
}
</script>

<style scoped>
.news-panel {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  height: fit-content;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 1rem;
}

.panel-title {
  font-size: 1.25rem;
  font-weight: bold;
  color: #fff;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.icon {
  font-size: 1.2em;
}

.count {
  font-size: 0.875rem;
  color: #888;
  font-weight: normal;
}

.refresh-btn {
  padding: 0.5rem;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(180deg);
}

.refresh-icon {
  font-size: 1rem;
  display: block;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 600px;
  overflow-y: auto;
}

.news-item {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem;
  padding: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.news-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.15);
}

.news-item.severity-critical {
  border-left-color: #dc2626;
}

.news-item.severity-high {
  border-left-color: #ea580c;
}

.news-item.severity-medium {
  border-left-color: #ca8a04;
}

.news-item.severity-low {
  border-left-color: #16a34a;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.category-tag {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #fff;
}

.category-apt {
  background: linear-gradient(135deg, #dc2626, #991b1b);
}

.category-breach {
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
}

.category-malware {
  background: linear-gradient(135deg, #ea580c, #c2410c);
}

.category-ics {
  background: linear-gradient(135deg, #0891b2, #0e7490);
}

.category-phishing {
  background: linear-gradient(135deg, #ca8a04, #a16207);
}

.category-default {
  background: linear-gradient(135deg, #6b7280, #4b5563);
}

.severity-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.severity-critical {
  background: rgba(220, 38, 38, 0.2);
  color: #fca5a5;
  border: 1px solid #dc2626;
}

.severity-high {
  background: rgba(234, 88, 12, 0.2);
  color: #fed7aa;
  border: 1px solid #ea580c;
}

.severity-medium {
  background: rgba(202, 138, 4, 0.2);
  color: #fde68a;
  border: 1px solid #ca8a04;
}

.severity-low {
  background: rgba(22, 163, 74, 0.2);
  color: #bbf7d0;
  border: 1px solid #16a34a;
}

.news-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #fff;
  margin: 0 0 0.5rem 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-summary {
  font-size: 0.75rem;
  color: #aaa;
  margin: 0 0 0.75rem 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: #888;
}

.news-source {
  font-weight: 500;
}

.news-time {
  color: #666;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .news-list {
    max-height: 400px;
  }
  
  .news-item {
    padding: 0.875rem;
  }
}

@media (max-width: 768px) {
  .news-panel {
    padding: 1rem;
  }
  
  .news-list {
    max-height: 500px;
  }
}
</style>