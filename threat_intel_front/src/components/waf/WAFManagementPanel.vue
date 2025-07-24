<template>
  <div class="management-section">
    <div class="collapsible-panel">
      <div class="panel-header" @click="togglePanel('lists')">
        <div class="panel-title">
          <i class="panel-icon fa fa-list-alt"></i>
          <span>黑白名单管理</span>
          <span class="panel-count">({{ whiteList.length + blackList.length }})</span>
        </div>
        <i class="collapse-icon" :class="{ collapsed: !panels.lists }">▼</i>
      </div>
      
      <div v-show="panels.lists" class="panel-content">
        <div class="lists-grid">
          <div class="list-section">
            <div class="list-header">
              <h4>白名单规则 ({{ whiteList.length }})</h4>
              <div class="list-actions">
                <button @click="$emit('fetchWhiteList')" class="mini-btn">
                  <i class="fa fa-refresh"></i>
                </button>
                <div class="pagination-controls">
                  <button @click="prevWhitePage" :disabled="whitePage <= 1" class="page-btn">
                    <i class="fa fa-chevron-left"></i>
                  </button>
                  <span class="page-info">{{ whitePage }} / {{ totalWhitePages }}</span>
                  <button @click="nextWhitePage" :disabled="whitePage >= totalWhitePages" class="page-btn">
                    <i class="fa fa-chevron-right"></i>
                  </button>
                </div>
              </div>
            </div>
            <div class="list-content">
              <div v-if="pagedWhiteList.length > 0" class="list-items-container"> <div v-for="item in pagedWhiteList" :key="item.rule_id" class="list-item white-item">
                  <div class="item-info">
                    <code>{{ item.rule_id }}</code>
                    <span>{{ item.rule_name || '未命名规则' }}</span>
                  </div>
                  <button @click="$emit('deleteWhite', item.rule_id)" class="delete-btn">
                    <i class="fa fa-trash"></i>
                  </button>
                </div>
              </div>
              <div v-else class="empty-list">
                <span>暂无白名单规则</span>
              </div>
            </div>
          </div>

          <div class="list-section">
            <div class="list-header">
              <h4>黑名单IP ({{ blackList.length }})</h4>
              <div class="list-actions">
                <button @click="$emit('fetchBlackList')" class="mini-btn">
                  <i class="fa fa-refresh"></i>
                </button>
                <div class="pagination-controls">
                  <button @click="prevBlackPage" :disabled="blackPage <= 1" class="page-btn">
                    <i class="fa fa-chevron-left"></i>
                  </button>
                  <span class="page-info">{{ blackPage }} / {{ totalBlackPages }}</span>
                  <button @click="nextBlackPage" :disabled="blackPage >= totalBlackPages" class="page-btn">
                    <i class="fa fa-chevron-right"></i>
                  </button>
                </div>
              </div>
            </div>
            <div class="list-content">
              <div v-if="pagedBlackList.length > 0" class="list-items-container"> <div v-for="(item, index) in pagedBlackList" :key="item.ip" class="list-item black-item">
                  <div class="item-info">
                    <code>{{ item.ip }}</code>
                    <span>{{ item.reason || '未指定原因' }}</span>
                  </div>
                  <button @click="$emit('deleteBlack', item.ip)" class="delete-btn">
                    <i class="fa fa-trash"></i>
                  </button>
                </div>
              </div>
              <div v-else class="empty-list">
                <span>暂无黑名单IP</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="collapsible-panel">
      <div class="panel-header" @click="togglePanel('operations')">
        <div class="panel-title">
          <i class="panel-icon fa fa-wrench"></i>
          <span>快速操作</span>
        </div>
        <i class="collapse-icon" :class="{ collapsed: !panels.operations }">▼</i>
      </div>
      
      <div v-show="panels.operations" class="panel-content">
        <div class="operations-grid">
          <div class="operation-card">
            <div class="operation-header">
              <i class="op-icon fa fa-shield"></i>
              <h4>添加白名单</h4>
            </div>
            <form @submit.prevent="addWhite" class="operation-form">
              <div class="form-group">
                <label>规则名称</label>
                <input :value="newWhiteName" @input="$emit('update:newWhiteName', $event.target.value)" placeholder="请输入规则名称" required />
              </div>
              <div class="form-group">
                <label>IP地址/范围</label>
                <input :value="newWhiteIP" @input="$emit('update:newWhiteIP', $event.target.value)" placeholder="例如: 192.168.1.0/24" required />
              </div>
              <div class="form-group">
                <label>备注</label>
                <input :value="newWhiteRemark" @input="$emit('update:newWhiteRemark', $event.target.value)" placeholder="可选" />
              </div>
              <button type="submit" :disabled="loading" class="submit-btn white">
                <i class="fa fa-plus mr-1"></i>添加白名单
              </button>
            </form>
          </div>

          <div class="operation-card">
            <div class="operation-header">
              <i class="op-icon fa fa-ban"></i>
              <h4>添加黑名单</h4>
            </div>
            <form @submit.prevent="addBlack" class="operation-form">
              <div class="form-group">
                <label>IP地址</label>
                <input :value="newBlackIP" @input="$emit('update:newBlackIP', $event.target.value)" placeholder="例如: 192.168.1.100" required />
              </div>
              <div class="form-group">
                <label>封禁原因</label>
                <select :value="newBlackReason" @change="$emit('update:newBlackReason', $event.target.value)">
                  <option value="恶意扫描">恶意扫描</option>
                  <option value="暴力破解">暴力破解</option>
                  <option value="SQL注入">SQL注入</option>
                  <option value="XSS攻击">XSS攻击</option>
                  <option value="CC攻击">CC攻击</option>
                  <option value="其他">其他</option>
                </select>
              </div>
              <div class="form-group">
                <label>封禁时长</label>
                <select :value="newBlackDuration" @change="$emit('update:newBlackDuration', $event.target.value)">
                  <option value="1h">1小时</option>
                  <option value="12h">12小时</option>
                  <option value="24h">24小时</option>
                  <option value="7d">7天</option>
                  <option value="30d">30天</option>
                  <option value="permanent">永久</option>
                </select>
              </div>
              <button type="submit" :disabled="loading" class="submit-btn black">
                <i class="fa fa-plus mr-1"></i>添加黑名单
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WAFManagementPanel',
  props: {
    whiteList: {
      type: Array,
      default: () => []
    },
    blackList: {
      type: Array,
      default: () => []
    },
    whitePage: {
      type: Number,
      default: 1
    },
    whitePageSize: {
      type: Number,
      default: 5
    },
    blackPage: {
      type: Number,
      default: 1
    },
    blackPageSize: {
      type: Number,
      default: 5
    },
    newWhiteName: {
      type: String,
      default: ''
    },
    newWhiteIP: {
      type: String,
      default: ''
    },
    newWhiteRemark: {
      type: String,
      default: ''
    },
    newBlackIP: {
      type: String,
      default: ''
    },
    newBlackReason: {
      type: String,
      default: '恶意扫描'
    },
    newBlackDuration: {
      type: String,
      default: '24h'
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      panels: {
        lists: true, // 默认展开列表面板
        operations: true // 默认展开操作面板
      },
    }
  },
  computed: {
    pagedWhiteList() {
      const start = (this.whitePage - 1) * this.whitePageSize
      return this.whiteList.slice(start, start + this.whitePageSize)
    },
    
    pagedBlackList() {
      const start = (this.blackPage - 1) * this.blackPageSize
      return this.blackList.slice(start, start + this.blackPageSize)
    },
    
    totalWhitePages() {
      // 确保至少有一页，即使列表为空
      return Math.ceil(this.whiteList.length / this.whitePageSize) || 1
    },
    
    totalBlackPages() {
      // 确保至少有一页，即使列表为空
      return Math.ceil(this.blackList.length / this.blackPageSize) || 1
    }
  },
  methods: {
    togglePanel(panelKey) {
      this.panels[panelKey] = !this.panels[panelKey]
    },
    prevWhitePage() {
      if (this.whitePage > 1) {
        this.$emit('update:whitePage', this.whitePage - 1)
      }
    },
    
    nextWhitePage() {
      if (this.whitePage < this.totalWhitePages) {
        this.$emit('update:whitePage', this.whitePage + 1)
      }
    },
    
    prevBlackPage() {
      if (this.blackPage > 1) {
        this.$emit('update:blackPage', this.blackPage - 1)
      }
    },
    
    nextBlackPage() {
      if (this.blackPage < this.totalBlackPages) {
        this.$emit('update:blackPage', this.blackPage + 1)
      }
    },

    addWhite() {
      if (!this.newWhiteName.trim() || !this.newWhiteIP.trim()) {
        this.$emit('showError', '请输入完整白名单信息');
        return;
      }
      const ipPattern = /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\/([0-9]|[1-2][0-9]|3[0-2]))?$/
      if (!ipPattern.test(this.newWhiteIP.trim())) {
        this.$emit('showError', '请输入有效的IP地址或CIDR范围')
        return;
      }
      this.$emit('addWhite');
    },

    addBlack() {
      if (!this.newBlackIP.trim()) {
        this.$emit('showError', '请输入黑名单IP');
        return;
      }
      const ipPattern = /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
      if (!ipPattern.test(this.newBlackIP.trim())) {
        this.$emit('showError', '请输入有效的IP地址')
        return;
      }
      this.$emit('addBlack');
    }
  },
  // 可以在这里添加mounted生命周期钩子，默认展开面板
  mounted() {
    this.panels.lists = true;
    this.panels.operations = true;
  }
}
</script>

<style scoped>
/* 可折叠面板 */
.collapsible-panel {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  margin-bottom: 1.5rem;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.collapsible-panel:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 1rem 1.5rem;
  user-select: none;
  font-weight: 700;
  font-size: 1rem;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: all 0.3s ease;
}

.panel-header:hover {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.panel-icon {
  font-size: 1.2rem;
}

.panel-count {
  font-size: 0.9rem;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.8);
  margin-left: 0.5rem;
}

.collapse-icon {
  transition: transform 0.3s ease;
  font-size: 1.2rem;
}

.collapse-icon.collapsed {
  transform: rotate(-90deg);
}

.panel-content {
  padding: 1rem 1.5rem;
  color: white;
}

/* 列表网格 */
.lists-grid {
  display: flex;
  gap: 1.25rem;
  flex-wrap: wrap;
}

/* 单个列表区域 */
.list-section {
  flex: 1;
  min-width: 280px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column; /* Changed to column flex container */
  height: 320px; /* Fixed height for the section to contain the scrollable content */
  overflow: hidden; /* Hide overflow of the section itself */
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
}

.list-section:hover {
  background: rgba(255, 255, 255, 0.08);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  flex-shrink: 0; /* Prevent header from shrinking */
}

.list-header h4 {
  margin: 0;
  font-weight: 700;
  font-size: 1rem;
  color: #667eea;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.list-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.mini-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.mini-btn:hover {
  color: #667eea;
  background: rgba(255, 255, 255, 0.1);
}

/* 分页控制 */
.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.7);
  width: 24px;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  min-width: 60px;
  text-align: center;
}

/* NEW: list-content takes up remaining space and handles its own scrolling */
.list-content {
  flex: 1; /* Allows list-content to grow and take remaining space */
  overflow-y: auto; /* Enables vertical scrolling for the content */
  padding-right: 0.25rem; /* Add some padding to prevent scrollbar from touching content */
  /* 移除 display: flex; flex-direction: column; */
}

/* 新增的容器，用于统一列表项的间距 */
.list-items-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem; /* 保持列表项之间的间距 */
}

/* list-items-container 的父元素 list-content 负责滚动 */
/* 原本的 list-items 样式可以移除或合并 */


.list-item {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.list-item:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateX(2px);
}

.white-item {
  color: rgba(56, 161, 105, 0.8);
}

.black-item {
  color: rgba(229, 62, 62, 0.8);
}

.item-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  flex: 1;
  min-width: 0;
}

.item-info code {
  background: rgba(0, 0, 0, 0.2);
  padding: 3px 6px;
  border-radius: 6px;
  font-family: monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-info span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 删除按钮 */
.delete-btn {
  background: #ff4d4f; /* 更鲜明的红色背景 */
  border: none;
  color: white; /* 按钮文字为白色，与红色背景形成对比 */
  padding: 0.4rem 0.9rem; /* 稍微增大按钮大小 */
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(255, 77, 79, 0.3); /* 添加阴影增加立体感 */
}

.delete-btn:hover {
  background: #ff7875; /* 鼠标悬停时颜色变浅 */
  transform: translateY(-2px); /* 悬停时上浮效果更明显 */
  box-shadow: 0 4px 8px rgba(255, 77, 79, 0.5); /* 悬停时阴影更明显 */
}

/* 空列表状态 */
.empty-list {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%; /* Make empty state fill available space */
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.9rem;
}

/* 快速操作网格 */
.operations-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

/* 操作卡片 */
.operation-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.operation-card:hover {
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.operation-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.op-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.operation-header h4 {
  margin: 0;
  font-weight: 700;
  font-size: 1rem;
}

/* 操作表单 */
.operation-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.form-group input,
.form-group select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: white;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.form-group input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.submit-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.submit-btn.white {
  background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
  color: white;
}

.submit-btn.white:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
}

.submit-btn.black {
  background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%);
  color: white;
}

.submit-btn.black:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(229, 62, 62, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 1200px) {
  .operations-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 800px) {
  .lists-grid {
    flex-direction: column;
  }
}
</style>