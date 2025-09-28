<template>
  <div class="log-container">
    <div class="log-header">
      <h3 class="log-heading">
        <i class="icon">📊</i>
        预测历史记录
      </h3>
      <div class="log-stats">
        <div class="stat-item">
          <span class="stat-number">{{ totalCount }}</span>
          <span class="stat-label">总记录</span>
        </div>
        <div class="stat-item phishing-stat">
          <span class="stat-number">{{ phishingCount }}</span>
          <span class="stat-label">钓鱼邮件</span>
        </div>
        <div class="stat-item safe-stat">
          <span class="stat-number">{{ safeCount }}</span>
          <span class="stat-label">安全邮件</span>
        </div>
      </div>
    </div>

    <div class="log-controls">
      <div class="filter-group">
        <label class="filter-label">筛选结果:</label>
        <select v-model="filterType" @change="updateFilteredLogs" class="filter-select">
          <option value="all">全部</option>
          <option value="phishing">仅钓鱼邮件</option>
          <option value="safe">仅安全邮件</option>
        </select>
      </div>
      <div class="search-group">
        <input
          v-model="searchKeyword"
          @input="updateFilteredLogs"
          placeholder="搜索邮件内容..."
          class="search-input"
        />
        <i class="search-icon">🔍</i>
      </div>
      <div class="action-group">
        <button @click="refreshLogs" class="refresh-btn">
          刷新
        </button>
        <button @click="deleteAllLogs" class="clear-btn">
          清空记录
        </button>
      </div>
    </div>
    
    <div v-if="filteredLogs.length > 0" class="pagination-info">
      显示 {{ startIndex + 1 }}-{{ endIndex }} 条，共 {{ filteredLogs.length }} 条
    </div>

    <div class="log-content">
      <div v-if="isLoading" class="loading-state">
        <i class="loading-icon">⏳</i>
        <p>正在加载历史记录...</p>
      </div>
      <div v-else-if="paginatedLogs.length === 0" class="log-empty">
        <i class="empty-icon">📭</i>
        <p>{{ searchKeyword || filterType !== 'all' ? '未找到匹配的记录' : '暂无历史记录' }}</p>
      </div>

      <div v-else v-for="(log, index) in paginatedLogs" :key="log.id" class="log-item">
        <div class="log-item-header">
          <div class="timestamp">
            <i class="time-icon">🕒</i>
            {{ formatTimestamp(log.timestamp) }}
          </div>
          <div class="result-badge" :class="{
            'phishing-badge': log.isPhishing,
            'safe-badge': !log.isPhishing
          }">
            <i class="result-icon">{{ log.isPhishing ? '🚨' : '✅' }}</i>
            {{ log.result }}
          </div>
        </div>

        <div class="log-item-body">
          <div class="probability-section">
            <div class="probability-bar-container">
              <div class="probability-label">威胁概率</div>
              <div class="probability-bar">
                <div
                  class="probability-fill"
                  :class="{
                    'high-risk': log.probability >= 0.7,
                    'medium-risk': log.probability >= 0.3 && log.probability < 0.7,
                    'low-risk': log.probability < 0.3
                  }"
                  :style="{ width: (log.probability * 100) + '%' }"
                ></div>
              </div>
              <div class="probability-value">{{ (log.probability * 100).toFixed(1) }}%</div>
            </div>
          </div>

          <div class="content-section">
            <div class="content-header">
              <span class="content-label">邮件内容</span>
              <button
                @click="toggleExpand(log.id)"
                class="expand-btn"
                :class="{ 'expanded': expandedItems.has(log.id) }"
              >
                {{ expandedItems.has(log.id) ? '收起' : '展开' }}
                <i class="arrow-icon">▶</i>
              </button>
            </div>
            <div class="email-content" :class="{ 'expanded': expandedItems.has(log.id) }">
              {{ log.content }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="totalPages > 1 && !isLoading" class="pagination">
      <button
        @click="currentPage = 1"
        :disabled="currentPage === 1"
        class="page-btn"
      >
        首页
      </button>
      <button
        @click="currentPage--"
        :disabled="currentPage === 1"
        class="page-btn"
      >
        上一页
      </button>

      <div class="page-numbers">
        <button
          v-for="page in visiblePages"
          :key="page"
          @click="currentPage = page"
          class="page-btn"
          :class="{ 'active': page === currentPage }"
        >
          {{ page }}
        </button>
      </div>

      <button
        @click="currentPage++"
        :disabled="currentPage === totalPages"
        class="page-btn"
      >
        下一页
      </button>
      <button
        @click="currentPage = totalPages"
        :disabled="currentPage === totalPages"
        class="page-btn"
      >
        尾页
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PredictionLog',
  data() {
    return {
      logs: [],
      currentPage: 1,
      pageSize: 10,
      filterType: 'all',
      searchKeyword: '',
      filteredLogs: [],
      expandedItems: new Set(),
      isLoading: true,
    };
  },
  computed: {
    processedLogs() {
      return this.logs.map((log) => {
        // 修正钓鱼邮件判断逻辑
        const isPhishing = log.result === 'Phishing' || log.result === '钓鱼邮件';
        const displayResult = isPhishing ? '钓鱼邮件' : '安全邮件';
        
        return {
          ...log,
          isPhishing,
          result: displayResult,
        };
      });
    },
    totalCount() {
      return this.processedLogs.length;
    },
    phishingCount() {
      return this.processedLogs.filter((log) => log.isPhishing).length;
    },
    safeCount() {
      return this.processedLogs.filter((log) => !log.isPhishing).length;
    },
    totalPages() {
      return Math.ceil(this.filteredLogs.length / this.pageSize);
    },
    startIndex() {
      return (this.currentPage - 1) * this.pageSize;
    },
    endIndex() {
      return Math.min(this.startIndex + this.pageSize, this.filteredLogs.length);
    },
    paginatedLogs() {
      return this.filteredLogs.slice(this.startIndex, this.endIndex);
    },
    visiblePages() {
      const pages = [];
      const start = Math.max(1, this.currentPage - 2);
      const end = Math.min(this.totalPages, this.currentPage + 2);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    },
  },
  watch: {
    logs: {
      handler() {
        this.updateFilteredLogs();
      },
      immediate: true,
    },
    currentPage() {
      this.expandedItems.clear();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
  },
  mounted() {
    this.refreshLogs();
  },
  methods: {
    async refreshLogs() {
      this.isLoading = true;
      try {
        const response = await fetch('/api/phishing/history');
        if (!response.ok) {
          throw new Error(`Error fetching history: ${response.statusText}`);
        }
        const data = await response.json();
        console.log('API Response:', data); // 调试用
        
        // 修正数据处理逻辑
        if (data.status === 'success') {
          if (Array.isArray(data.data)) {
            // 处理数组格式的数据
            this.logs = data.data.map(item => {
              if (Array.isArray(item)) {
                // 如果是数组格式 [id, timestamp, result, probability, content]
                return {
                  id: item[0],
                  timestamp: new Date(item[1]).getTime(),
                  result: item[2],
                  probability: parseFloat(item[3]) || 0,
                  content: item[4] || '',
                };
              } else {
                // 如果是对象格式
                return {
                  id: item.id,
                  timestamp: new Date(item.timestamp).getTime(),
                  result: item.result,
                  probability: parseFloat(item.probability) || 0,
                  content: item.email_content || item.content || '',
                };
              }
            });
          } else if (typeof data.data === 'object' && data.data !== null) {
            // 如果返回的是单个对象，转换为数组
            this.logs = [{
              id: data.data.id,
              timestamp: new Date(data.data.timestamp).getTime(),
              result: data.data.result,
              probability: parseFloat(data.data.probability) || 0,
              content: data.data.email_content || data.data.content || '',
            }];
          } else {
            this.logs = [];
          }
        } else {
          console.error('API returned non-success status:', data);
          this.logs = [];
        }
      } catch (error) {
        console.error("无法获取预测历史记录:", error);
        this.logs = [];
      } finally {
        this.isLoading = false;
      }
    },
    async deleteAllLogs() {
      const userConfirmed = confirm("您确定要清空所有历史记录吗？此操作不可逆。");
      if (!userConfirmed) {
          return;
      }
      this.isLoading = true;
      try {
        const response = await fetch('/api/phishing/clear', {
          method: 'GET',
        });
        if (!response.ok) {
          throw new Error(`Error clearing history: ${response.statusText}`);
        }
        const result = await response.json();
        console.log('Clear result:', result);
        await this.refreshLogs();
      } catch (error) {
        console.error("无法清空历史记录:", error);
        alert("清空记录失败，请稍后重试");
      } finally {
        this.isLoading = false;
      }
    },
    updateFilteredLogs() {
      let filtered = [...this.processedLogs];
      if (this.filterType === 'phishing') {
        filtered = filtered.filter((log) => log.isPhishing);
      } else if (this.filterType === 'safe') {
        filtered = filtered.filter((log) => !log.isPhishing);
      }
      if (this.searchKeyword.trim()) {
        const keyword = this.searchKeyword.trim().toLowerCase();
        filtered = filtered.filter((log) => 
          log.content.toLowerCase().includes(keyword)
        );
      }
      this.filteredLogs = filtered;
      this.currentPage = 1;
    },
    formatTimestamp(timestamp) {
      if (!timestamp || isNaN(timestamp)) {
        return '无效时间';
      }
      
      const date = new Date(timestamp);
      const now = new Date();
      const diff = now - date;

      if (diff < 60000) {
        return '刚刚';
      } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分钟前`;
      } else if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}小时前`;
      } else {
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
        });
      }
    },
    toggleExpand(id) {
      if (this.expandedItems.has(id)) {
        this.expandedItems.delete(id);
      } else {
        this.expandedItems.add(id);
      }
    },
  },
};
</script>

<style scoped>
.log-container {
  margin-top: 40px;
  padding: 24px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.log-heading {
  display: flex;
  align-items: center;
  font-size: 1.75rem;
  margin: 0;
  color: #2d3748;
  font-weight: 700;
  gap: 8px;
}

.icon {
  font-size: 1.5rem;
}

.log-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 12px 16px;
  border-radius: 12px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  min-width: 80px;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #4a5568;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: #718096;
  margin-top: 2px;
}

.phishing-stat .stat-number {
  color: #e53e3e;
}

.safe-stat .stat-number {
  color: #38a169;
}

.log-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filter-group, .search-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
}

.filter-select {
  padding: 8px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  transition: all 0.2s;
}

.filter-select:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.search-group {
  position: relative;
}

.search-input {
  padding: 8px 40px 8px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  width: 200px;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #a0aec0;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.clear-btn {
  padding: 8px 16px;
  border: none;
  background: #f56565;
  color: white;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #e53e3e;
  box-shadow: 0 4px 12px rgba(229, 62, 62, 0.2);
}

.refresh-btn {
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  background: white;
  color: #4a5568;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover {
  border-color: #4299e1;
  color: #2b6cb0;
  background: #ebf8ff;
}

.pagination-info {
  font-size: 14px;
  color: #718096;
  text-align: right;
  margin-bottom: 12px;
}

.log-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  /* 新增或修改以下两行 */
  max-height: 300px; /* 估算三条记录的高度，请根据实际效果调整 */
  overflow-y: auto;  /* 启用垂直滚动条 */
}

.log-empty {
  text-align: center;
  padding: 60px 20px;
  color: #a0aec0;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  display: block;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #718096;
}

.loading-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  display: block;
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.log-item {
  border-bottom: 1px solid #f7fafc;
  transition: all 0.2s;
}

.log-item:hover {
  background: #f8f9fa;
}

.log-item:last-child {
  border-bottom: none;
}

.log-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 12px;
}

.timestamp {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #718096;
}

.time-icon {
  font-size: 12px;
}

.result-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.phishing-badge {
  background: linear-gradient(135deg, #fed7d7, #feb2b2);
  color: #c53030;
}

.safe-badge {
  background: linear-gradient(135deg, #c6f6d5, #9ae6b4);
  color: #276749;
}

.result-icon {
  font-size: 12px;
}

.log-item-body {
  padding: 0 20px 16px;
}

.probability-section {
  margin-bottom: 16px;
}

.probability-bar-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.probability-label {
  font-size: 13px;
  color: #4a5568;
  font-weight: 500;
  min-width: 60px;
}

.probability-bar {
  flex: 1;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  position: relative;
}

.probability-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.high-risk {
  background: linear-gradient(90deg, #fc8181, #e53e3e);
}

.medium-risk {
  background: linear-gradient(90deg, #f6ad55, #ed8936);
}

.low-risk {
  background: linear-gradient(90deg, #68d391, #38a169);
}

.probability-value {
  font-size: 13px;
  font-weight: 600;
  color: #4a5568;
  min-width: 45px;
  text-align: right;
}

.content-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.content-label {
  font-size: 13px;
  font-weight: 500;
  color: #4a5568;
}

.expand-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: #4299e1;
  font-size: 12px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.expand-btn:hover {
  background: #ebf8ff;
  color: #2b6cb0;
}

.arrow-icon {
  transition: transform 0.2s;
  font-size: 10px;
}

.expand-btn.expanded .arrow-icon {
  transform: rotate(90deg);
}

.email-content {
  font-size: 14px;
  line-height: 1.5;
  color: #2d3748;
  background: white;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  max-height: 60px;
  overflow: hidden;
  transition: max-height 0.3s ease;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.email-content.expanded {
  max-height: 400px;
  overflow-y: auto;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 24px;
  flex-wrap: wrap;
}

.page-btn {
  padding: 8px 12px;
  border: 2px solid #e2e8f0;
  background: white;
  color: #4a5568;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  min-width: 40px;
}

.page-btn:hover:not(:disabled) {
  border-color: #4299e1;
  color: #2b6cb0;
  background: #ebf8ff;
}

.page-btn.active {
  background: #4299e1;
  color: white;
  border-color: #4299e1;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .log-container {
    padding: 16px;
    margin-top: 20px;
  }
  
  .log-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .log-stats {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .log-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    width: 100%;
  }
  
  .log-item-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .probability-bar-container {
    flex-direction: column;
    align-items: stretch;
    gap: 6px;
  }
  
  .pagination {
    gap: 4px;
  }
  
  .page-btn {
    padding: 6px 8px;
    font-size: 12px;
    min-width: 32px;
  }
}
</style>