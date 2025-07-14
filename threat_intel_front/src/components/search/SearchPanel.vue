<template>
  <div class="search-panel">
    <div class="panel-header">
      <h2>
        <i class="fas fa-search"></i>
        威胁情报查询
      </h2>
    </div>
    
    <!-- 搜索标签 -->
    <div class="search-tabs">
      <button 
        v-for="tab in tabs"
        :key="tab.type"
        :class="['tab', { active: activeTab === tab.type }]"
        @click="selectTab(tab.type)"
      >
        <i :class="tab.icon"></i>
        <span>{{ tab.label }}</span>
      </button>
    </div>
    
    <!-- 搜索输入 -->
    <div class="search-input-group">
      <div class="input-wrapper">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="getPlaceholder()"
          class="search-input"
          @keyup.enter="handleSearch"
          :disabled="loading"
        />
        <i class="fas fa-search input-icon"></i>
      </div>
      
      <button 
        class="search-btn"
        @click="handleSearch"
        :disabled="loading || !searchQuery.trim()"
      >
        <i v-if="loading" class="fas fa-spinner fa-spin"></i>
        <span>{{ loading ? '查询中...' : '查询' }}</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchPanel',
  props: {
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['search', 'tab-change'],
  data() {
    return {
      activeTab: 'ip',
      searchQuery: '',
      tabs: [
        {
          type: 'ip',
          label: 'IP',
          icon: 'fas fa-server'
        },
        {
          type: 'url',
          label: 'URL',
          icon: 'fas fa-globe'
        },
        {
          type: 'file',
          label: 'FILE',
          icon: 'fas fa-file'
        }
      ]
    }
  },
  methods: {
    selectTab(type) {
      this.activeTab = type
      this.$emit('tab-change', type)
    },
    
    handleSearch() {
      if (!this.searchQuery.trim()) return
      
      this.$emit('search', {
        query: this.searchQuery,
        type: this.activeTab
      })
    },
    
    getPlaceholder() {
      const placeholders = {
        ip: '输入IP地址进行查询...',
        url: '输入URL地址进行查询...',
        file: '输入文件哈希进行查询...'
      }
      return placeholders[this.activeTab] || '输入查询内容...'
    }
  }
}
</script>

<style scoped>
.search-panel {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 1rem;
  padding: 1.5rem;
}

.panel-header h2 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
  margin: 0 0 1.5rem 0;
}

.panel-header i {
  color: #8b5cf6;
}

.search-tabs {
  display: flex;
  gap: 0.25rem;
  background: rgba(30, 41, 59, 0.5);
  padding: 0.25rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  background: transparent;
  color: #a855f7;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab:hover {
  color: white;
  background: rgba(71, 85, 105, 0.5);
}

.tab.active {
  background: #8b5cf6;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-input-group {
  display: flex;
  gap: 0.75rem;
}

.input-wrapper {
  flex: 1;
  position: relative;
}

.search-input {
  width: 100%;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid #374151;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  padding-right: 2.5rem;
  color: white;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.search-input::placeholder {
  color: #9ca3af;
}

.search-input:focus {
  outline: none;
  border-color: #8b5cf6;
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
}

.search-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  pointer-events: none;
}

.search-btn {
  background: linear-gradient(45deg, #8b5cf6, #06b6d4);
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.search-btn:hover:not(:disabled) {
  background: linear-gradient(45deg, #7c3aed, #0891b2);
  transform: translateY(-1px);
}

.search-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 640px) {
  .search-input-group {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .search-btn {
    justify-content: center;
  }
}
</style>