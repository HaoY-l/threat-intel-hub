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
        @click="handleSearchAgain(item)"
      >
        <div class="history-content">
          <div class="history-info">
            <i :class="getTypeIcon(item.type)"></i>
            <code class="history-query">{{ item.query }}</code>
            <span class="result-count">{{ item.results }} 结果</span>
          </div>
          <span class="history-time">{{ formatTime(item.timestamp) }}</span>
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
  methods: {
    getTypeIcon(type) {
      const iconMap = {
        'ip': 'fas fa-server',
        'url': 'fas fa-globe',
        'file': 'fas fa-file'
      }
      return iconMap[type] || 'fas fa-search'
    },
    
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN')
    },
    
    handleSearchAgain(item) {
      this.$emit('search-again', {
        query: item.query,
        type: item.type
      })
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
  max-height: 12rem;
  overflow-y: auto;
}

.history-list::-webkit-scrollbar {
  width: 4px;
}

.history-list::-webkit-scrollbar-track {
  background: rgba(30, 41, 59, 0.5);
  border-radius: 2px;
}

.history-list::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.5);
  border-radius: 2px;
}

.history-item {
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid rgba(71, 85, 105, 0.3);
  border-radius: 0.5rem;
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.history-item:hover {
  border-color: rgba(139, 92, 246, 0.5);
  background: rgba(30, 41, 59, 0.5);
}

.history-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.history-info i {
  color: #8b5cf6;
  width: 1rem;
}

.history-query {
  color: #06b6d4;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}

.result-count {
  color: #a855f7;
  font-size: 0.75rem;
}

.history-time {
  color: #9ca3af;
  font-size: 0.75rem;
}

@media (max-width: 640px) {
  .history-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .history-info {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}
</style>