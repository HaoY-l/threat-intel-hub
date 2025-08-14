<template>
  <div class="news-list">
    <div class="list-header">
      <h2>
        <i class="fas fa-newspaper"></i>
        安全资讯
      </h2>
      <div class="count">{{ newsData.length }} 条记录</div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>正在获取最新资讯...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!newsData || newsData.length === 0" class="empty-container">
      <i class="fas fa-newspaper"></i>
      <p>暂无新闻数据</p>
      <button @click="$emit('refresh')" class="refresh-btn">
        <i class="fas fa-sync-alt"></i>
        刷新数据
      </button>
    </div>

    <!-- 新闻列表 -->
    <div v-else class="news-items">
      <div
        v-for="news in newsData"
        :key="news.id"
        class="news-card"
        @click="openNewsDetail(news)"
      >
        <div class="card-header">
          <div class="news-info">
            <span class="source">{{ news.source || '未知来源' }}</span>
            <span class="category-tag" :class="getCategoryClass(news.category)">
              {{ news.category || '未分类' }}
            </span>
          </div>
          <span class="date">{{ formatDate(news.time) }}</span>
        </div>

        <h3 class="title" :title="news.title">{{ news.title || '无标题' }}</h3>
        <p class="description" :title="news.summary">
          {{ news.summary || '暂无描述信息...' }}
        </p>

        <div class="card-footer">
          <span></span>
          <i class="fas fa-chevron-right"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "NewsPanel",
  props: {
    newsData: { type: Array, default: () => [] },
    isLoading: { type: Boolean, default: false }
  },
  emits: ['refresh'],
  methods: {
    getCategoryClass(category) {
      const classes = {
        'APT攻击': 'category-red',
        '数据泄露': 'category-blue',
        '恶意软件': 'category-orange',
        '工控安全': 'category-purple',
        '钓鱼攻击': 'category-green',
        '网络安全': 'category-cyan',
        '漏洞预警': 'category-yellow'
      }
      return classes[category] || 'category-gray'
    },
    openNewsDetail(news) {
      if (news.url) window.open(news.url, "_blank")
    },
    formatDate(dateString) {
      if (!dateString) return '未知时间'
      try {
        return new Date(dateString).toLocaleDateString("zh-CN")
      } catch {
        return dateString
      }
    }
  }
}
</script>

<style scoped>
.news-list {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 1rem;
  padding: 1.5rem;
  height: fit-content;
}

/* 头部标题样式对齐 CVE */
.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.list-header h2 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
  margin: 0;
}

.list-header i {
  color: #06b6d4;
}

.count {
  font-size: 0.875rem;
  color: #a855f7;
}

/* 加载 & 空状态 */
.loading-container, .empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #a855f7;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(168, 85, 247, 0.3);
  border-top: 3px solid #a855f7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

.empty-container i {
  font-size: 3rem;
  color: #374151;
}

.refresh-btn {
  background: rgba(168, 85, 247, 0.8);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(168, 85, 247, 1);
  transform: translateY(-1px);
}

/* 新闻列表滚动区域 */
.news-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 38rem;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.news-items::-webkit-scrollbar {
  width: 4px;
}
.news-items::-webkit-scrollbar-track {
  background: rgba(30, 41, 59, 0.5);
  border-radius: 2px;
}
.news-items::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.5);
  border-radius: 2px;
}
.news-items::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.8);
}

/* 新闻卡片样式，和 CVE 高度一致 */
.news-card {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(71, 85, 105, 0.5);
  border-radius: 0.5rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 120px;
  min-width: 280px; /* 新增：设定最小宽度，防止被挤压过小 */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.news-card:hover {
  border-color: rgba(139, 92, 246, 0.5);
  transform: translateY(-1px);
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.news-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-tag {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: white;
}

.category-red { background: #ef4444; }
.category-blue { background: #3b82f6; }
.category-orange { background: #f97316; }
.category-purple { background: #8b5cf6; }
.category-green { background: #10b981; }
.category-cyan { background: #06b6d4; }
.category-yellow { background: #f59e0b; }
.category-gray { background: #6b7280; }

.date {
  font-size: 0.75rem;
  color: #a855f7;
}

/* 标题 & 描述对齐 CVE 样式 */
.title {
  color: white;
  font-size: 1rem;
  font-weight: 500;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1; 
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