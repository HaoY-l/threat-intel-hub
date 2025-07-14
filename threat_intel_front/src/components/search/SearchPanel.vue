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

    <!-- 文件上传，仅 file 类型可见 -->
    <div v-if="activeTab === 'file'" class="file-upload">
      <label>
        <input type="file" @change="handleFileUpload" />
        <i class="fas fa-upload"></i>
        上传文件自动计算 SHA256
      </label>
    </div>

    <!-- 验证提示 -->
    <div v-if="validationError" class="validation-error">
      <i class="fas fa-exclamation-triangle"></i>
      {{ validationError }}
    </div>
  </div>
</template>

<script>
import { sha256 } from 'js-sha256'

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
      validationError: '',
      tabs: [
        { type: 'ip', label: 'IP', icon: 'fas fa-server' },
        { type: 'url', label: 'URL', icon: 'fas fa-globe' },
        { type: 'file', label: 'FILE', icon: 'fas fa-file' }
      ]
    }
  },
  watch: {
    searchQuery() {
      this.validationError = ''
    }
  },
  methods: {
    selectTab(type) {
      this.activeTab = type
      this.searchQuery = ''
      this.validationError = ''
      this.$emit('tab-change', type)
    },
    validateInput() {
      const query = this.searchQuery.trim()
      if (!query) {
        this.validationError = '请输入查询内容'
        return false
      }
      switch (this.activeTab) {
        case 'ip':
          if (!this.isValidIP(query)) {
            this.validationError = '请输入有效的IP地址'
            return false
          }
          break
        case 'url':
          if (!this.isValidURL(query)) {
            this.validationError = '请输入有效的URL地址'
            return false
          }
          break
        case 'file':
          if (!this.isValidHash(query)) {
            this.validationError = '请输入有效的文件哈希值（MD5、SHA1或SHA256）'
            return false
          }
          break
      }
      return true
    },
    isValidIP(ip) {
      const ipRegex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
      return ipRegex.test(ip)
    },
    isValidURL(url) {
      try {
        new URL(url.startsWith('http') ? url : 'http://' + url)
        return true
      } catch {
        return false
      }
    },
    isValidHash(hash) {
      const md5Regex = /^[a-fA-F0-9]{32}$/
      const sha1Regex = /^[a-fA-F0-9]{40}$/
      const sha256Regex = /^[a-fA-F0-9]{64}$/
      return md5Regex.test(hash) || sha1Regex.test(hash) || sha256Regex.test(hash)
    },
    async handleFileUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      const arrayBuffer = await file.arrayBuffer()
      const hash = sha256(new Uint8Array(arrayBuffer))
      this.searchQuery = hash
      this.validationError = ''
    },
    handleSearch() {
      if (!this.validateInput()) return
      this.$emit('search', {
        query: this.searchQuery.trim(),
        type: this.activeTab
      })
    },
    getPlaceholder() {
      const placeholders = {
        ip: '输入IP地址进行查询... (例: 192.168.1.1)',
        url: '输入URL地址进行查询... (例: example.com)',
        file: '输入文件哈希进行查询... (MD5/SHA1/SHA256)'
      }
      return placeholders[this.activeTab] || '输入查询内容...'
    },
    setSearchQuery(query, type) {
      this.activeTab = type
      this.searchQuery = query
      this.validationError = ''
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

.validation-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 0.375rem;
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

.file-upload {
  margin-top: 1rem;
  color: #8b5cf6;
  font-size: 0.875rem;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.file-upload input {
  display: none;
}
.file-upload label {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>
