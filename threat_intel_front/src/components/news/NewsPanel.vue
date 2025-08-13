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
        @click="openNewsDetail(news)"
      >
        <div class="news-header">
          <span class="category-tag" :class="getCategoryClass(news.category)">
            {{ news.category }}
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
    // 危险等级相关的getSeverityClass方法已被移除
    getCategoryClass(category) {
      const classes = {
        'APT攻击': 'category-apt',
        '数据泄露': 'category-breach',
        '恶意软件': 'category-malware',
        '工控安全': 'category-ics',
        '钓鱼攻击': 'category-phishing',
        '网络安全': 'category-default' // 添加一个默认分类以匹配后端返回的数据
      }
      return classes[category] || 'category-default'
    },

    openNewsDetail(news) {
      // 点击新闻项时直接跳转到新闻链接
      if (news.url) {
        window.open(news.url, '_blank');
      }
    },

    refreshNews() {
      this.$emit('refresh')
    }
  }
}
</script>

<style scoped>
/* 样式保持不变 */
.news-panel {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.panel-title {
  color: #fff;
  font-size: 1.25rem;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.panel-title .icon {
  margin-right: 0.5rem;
  font-size: 1.5rem;
}

.panel-title .count {
  font-size: 0.875rem;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.6);
  margin-left: 0.5rem;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(360deg);
}

.refresh-icon {
  font-size: 1rem;
  color: #fff;
}

.news-list {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.news-list::-webkit-scrollbar {
  display: none;
}

.news-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid transparent;
}

.news-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.1);
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.category-tag {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #fff;
}

.category-apt {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.category-breach {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.category-malware {
  background: linear-gradient(135deg, #f97316, #ea580c);
}

.category-ics {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.category-phishing {
  background: linear-gradient(135deg, #10b981, #059669);
}

.category-default {
  background: linear-gradient(135deg, #6b7280, #4b5563);
}

.news-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #fff;
  margin: 0 0 0.5rem 0;
}

.news-summary {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 0.5rem;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.5);
}

.news-source {
  font-weight: 500;
}
</style>