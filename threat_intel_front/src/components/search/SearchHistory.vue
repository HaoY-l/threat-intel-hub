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
        :class="{ 'expanded': item.expanded }"
      >
        <div class="history-content" @click="toggleHistoryDetails(item)">
          <div class="history-info">
            <code class="history-query" :title="item.query">{{ item.query }}</code>
            <span class="result-count">{{ item.results || 0 }} 结果</span>
            
            <!-- 威胁等级徽章 - 添加默认值用于测试 -->
            <span 
              class="threat-level-badge"
              :class="getThreatLevelClass(item.maxThreatLevel || getDefaultThreatLevel(item))"
            >
              {{ getThreatLevelText(item.maxThreatLevel || getDefaultThreatLevel(item)) }}
            </span>
            
            <!-- 风险分数徽章 - 添加默认值用于测试 -->
            <span 
              class="risk-score-badge"
              :class="getScoreClass(item.maxScore !== undefined ? item.maxScore : getDefaultScore(item))"
            >
              风险: {{ item.maxScore !== undefined ? item.maxScore : getDefaultScore(item) }}
            </span>
          </div>
          
          <div class="history-actions">
            <span class="history-time">{{ formatTime(item.timestamp) }}</span>
            <button 
              class="action-btn search-again-btn"
              @click.stop="handleSearchAgain(item)"
              title="重新查询"
            >
              <i class="fas fa-redo"></i>
            </button>
            <button 
              class="action-btn expand-btn"
              @click.stop="toggleHistoryDetails(item)"
              title="查看详情"
            >
              <i class="fas fa-chevron-down" :class="{ 'rotated': item.expanded }"></i>
            </button>
          </div>
        </div>

        <div v-if="item.expanded && item.detailResults" class="history-details-container">
          <div class="details-stats-bar">
            <span class="stat-item">
              <i class="fas fa-database"></i>
              {{ getUniqueSourcesCount(item.detailResults) }} 个数据源
            </span>
            <span class="stat-item">
              <i class="fas fa-shield-alt"></i>
              平均分: {{ getAverageScore(item.detailResults) }}
            </span>
          </div>

          <div class="results-container">
            <div 
              v-for="(result, index) in item.detailResults" 
              :key="index"
              class="result-item"
            >
              <div class="result-header">
                <div class="result-info">
                  <i :class="getTypeIcon(item.type)" class="type-icon"></i>
                  <code 
                    class="result-id" 
                    :title="getDisplayId(result, item.type)"
                  >
                    {{ getDisplayId(result, item.type) }}
                  </code>
                  <span 
                    class="threat-badge" 
                    :class="getThreatLevelClass(result.threat_level)"
                  >
                    {{ getThreatLevelText(result.threat_level) }}
                  </span>
                </div>
                <div class="score-section">
                  <span class="score-value" :class="getScoreClass(result.reputation_score)">
                    {{ result.reputation_score || 0 }}
                  </span>
                </div>
              </div>

              <div class="result-details">
                <div class="detail-row">
                  <span class="label">数据源:</span>
                  <span class="value">{{ result.source || '未知' }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">更新时间:</span>
                  <span class="value">{{ formatDate(result.last_update) }}</span>
                </div>
                <div v-if="item.type === 'url'" class="detail-row">
                  <span class="label">目标URL:</span>
                  <span class="value url-value">{{ result.target_url || result.id }}</span>
                </div>
                <div v-if="item.type === 'file'" class="detail-row">
                  <span class="label">文件哈希:</span>
                  <span class="value hash-value">{{ result.id }}</span>
                </div>
              </div>

              <div v-if="result.details" class="raw-data-toggle">
                <button 
                  class="toggle-btn"
                  @click="toggleRawDetails(item.id, index)"
                  :class="{ 'active': isRawDetailsExpanded(item.id, index) }"
                >
                  <i class="fas fa-code"></i>
                  <span>{{ isRawDetailsExpanded(item.id, index) ? '收起' : '展开' }}原始数据</span>
                  <i class="fas fa-chevron-down toggle-icon" :class="{ 'rotated': isRawDetailsExpanded(item.id, index) }"></i>
                </button>
              </div>

              <div v-if="isRawDetailsExpanded(item.id, index) && result.details" class="raw-details-wrapper">
                <pre class="raw-details">{{ formatDetails(result.details) }}</pre>
                <button @click="copyDetails(result.details)" class="copy-btn" title="复制详细信息">
                  <i class="fas fa-copy"></i>
                </button>
              </div>

            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchHistory',
  props: { history: { type: Array, default: () => [] } },
  emits: ['search-again', 'copy-success'],
  data() { return { expandedRawDetails: new Set() } },
  methods: {
    getTypeIcon(type){ const map={ip:'fas fa-server',url:'fas fa-globe',file:'fas fa-file'}; return map[type]||'fas fa-search'; },
    getThreatLevelClass(level){ const map={malicious:'threat-malicious',suspicious:'threat-suspicious',harmless:'threat-harmless',clean:'threat-harmless'}; return map[level]||'threat-unknown'; },
    getThreatIcon(level){ const map={malicious:'fas fa-skull-crossbones',suspicious:'fas fa-exclamation-triangle',harmless:'fas fa-shield-alt',clean:'fas fa-shield-alt'}; return map[level]||'fas fa-question-circle'; },
    getThreatLevelText(level){ const map={malicious:'恶意',suspicious:'可疑',harmless:'无害',clean:'清洁'}; return map[level]||'未知'; },
    getScoreClass(score){ const s=parseInt(score)||0; if(s>0) return'score-high'; if(s<0)return'score-low'; return'score-neutral'; },
    getDefaultThreatLevel(item) {
      // 根据查询内容或其他条件返回默认威胁等级
      if (item.query && (item.query.includes('malware') || item.query.includes('virus'))) {
        return 'malicious';
      }
      if (item.results && item.results > 5) {
        return 'suspicious';
      }
      return 'harmless';
    },
    getDefaultScore(item) {
      // 根据查询内容或其他条件返回默认风险分数
      if (item.query && (item.query.includes('malware') || item.query.includes('virus'))) {
        return 5;
      }
      if (item.results && item.results > 5) {
        return -1;
      }
      return 0;
    },
    getDisplayId(result,type){return type==='url'?result.target_url||result.id:result.id;},
    formatTime(ts){ const date=new Date(ts); const year=date.getFullYear(),month=String(date.getMonth()+1).padStart(2,'0'),day=String(date.getDate()).padStart(2,'0'),hours=String(date.getHours()).padStart(2,'0'),minutes=String(date.getMinutes()).padStart(2,'0'),seconds=String(date.getSeconds()).padStart(2,'0'); return`${year}/${month}/${day} ${hours}:${minutes}:${seconds}`; },
    formatDate(d){if(!d)return'未知';try{return new Date(d).toLocaleString('zh-CN');}catch{return'格式错误';}},
    formatDetails(details){if(!details)return'';try{return JSON.stringify(details,null,2);}catch{return String(details);}},
    toggleHistoryDetails(item){if(!('expanded'in item)) item.expanded=false; item.expanded=!item.expanded;},
    toggleRawDetails(hid,index){const key=`${hid}_${index}`;this.expandedRawDetails.has(key)?this.expandedRawDetails.delete(key):this.expandedRawDetails.add(key);},
    isRawDetailsExpanded(hid,index){return this.expandedRawDetails.has(`${hid}_${index}`);},
    handleSearchAgain(item){this.$emit('search-again',{query:item.query,type:item.type});},
    getUniqueSourcesCount(results){return new Set(results.map(r=>r.source)).size;},
    getAverageScore(results){if(!results||!results.length)return 0; return Math.round(results.reduce((sum,r)=>sum+(r.reputation_score||0),0)/results.length);},
    async copyDetails(details){try{await navigator.clipboard.writeText(JSON.stringify(details,null,2));this.$emit('copy-success')}catch(e){console.error('复制失败:',e)}}
  }
}
</script>

<style scoped>
/* 整个组件的容器 */
.search-history {
  background: #100f1c;
  color: #f3f4f6;
  border-radius: 0.5rem;
  padding: 1rem;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  max-width: 600px;
}

/* 头部样式 */
.history-header {
  font-size: 1.25rem;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 1rem;
  padding-left: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.history-header i {
  color: #8b5cf6;
}

/* 历史记录列表容器 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* 单个历史记录项 */
.history-item {
  background: rgba(30, 32, 53, 0.5);
  border: 1px solid rgba(139, 92, 246, 0.1);
  border-radius: 0.5rem;
  padding: 0.6rem 0.8rem;
  transition: all 0.2s ease;
  cursor: pointer;
}
.history-item:hover {
  background: rgba(30, 32, 53, 0.7);
}

/* 展开时的样式 */
.history-item.expanded {
  background: #1e293b;
  border-color: #3c4a60;
}

/* 历史记录内容 */
.history-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 左侧信息区域 */
.history-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

/* 查询内容（IP/域名等） */
.history-query {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  font-weight: bold;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 250px;
}

/* 结果数 */
.result-count {
  color: #a78bfa;
  font-size: 0.75rem;
  margin-right: 0.5rem;
  white-space: nowrap;
}

/* 威胁等级徽章 - 优化样式匹配图片效果 */
.threat-level-badge {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
  color: #fff;
  white-space: nowrap;
  text-transform: none;
  letter-spacing: 0;
  line-height: 1.2;
  border: none;
}
.threat-level-badge.threat-malicious {
  background: #dc2626;
  color: #fff;
}
.threat-level-badge.threat-suspicious {
  background: #ea580c;
  color: #fff;
}
.threat-level-badge.threat-harmless,
.threat-level-badge.threat-clean {
  background: #16a34a;
  color: #fff;
}
.threat-level-badge.threat-unknown {
  background: #64748b;
  color: #fff;
}

/* 风险分数徽章 - 优化样式匹配图片效果 */
.risk-score-badge {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
  white-space: nowrap;
  text-transform: none;
  letter-spacing: 0;
  line-height: 1.2;
  border: none;
}
.risk-score-badge.score-high {
  background: #dc2626;
  color: #fff;
}
.risk-score-badge.score-low {
  background: #16a34a;
  color: #fff;
}
.risk-score-badge.score-neutral {
  background: #ea580c;
  color: #fff;
}

/* 右侧操作区域 */
.history-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 时间戳 */
.history-time {
  color: #888;
  font-size: 0.75rem;
  white-space: nowrap;
}

/* 按钮样式 */
.action-btn {
  background: rgba(71, 85, 105, 0.3);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 0.25rem;
  padding: 0.25rem 0.4rem;
  color: #a855f7;
  cursor: pointer;
  font-size: 0.65rem;
  transition: all 0.2s ease;
}
.action-btn:hover {
  background: rgba(139, 92, 246, 0.3);
  border-color: rgba(139, 92, 246, 0.7);
}

/* 展开按钮的箭头动画 */
.expand-btn i.rotated {
  transform: rotate(180deg);
}

/* --- 详细信息部分样式（保持不变） --- */
.history-details-container {
  padding: 0.75rem 0.5rem 0 0.5rem;
  border-top: 1px solid rgba(147, 197, 253, 0.1);
  margin-top: 0.5rem;
}
.details-stats-bar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 0.75rem;
  font-size: 0.8rem;
  color: #94a3b8;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(147, 197, 253, 0.1);
}
.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.results-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.result-item {
  background: #1e293b;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #3c4a60;
  transition: all 0.2s ease;
}
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(147, 197, 253, 0.1);
}
.result-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}
.result-info .type-icon {
  color: #93c5fd;
  font-size: 1rem;
  width: auto;
}
.result-id {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
  font-size: 0.85rem;
  color: #93c5fd;
  word-break: break-all;
}
.threat-badge {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 0.25rem;
  color: #fff;
  white-space: nowrap;
}
.threat-badge.threat-malicious { background: #dc2626; }
.threat-badge.threat-suspicious { background: #ea580c; }
.threat-badge.threat-harmless { background: #16a34a; }
.threat-badge.threat-unknown { background: #64748b; }
.score-section {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.score-value {
  font-size: 1.1rem;
  font-weight: 700;
  line-height: 1;
}
.result-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.8rem;
}
.detail-row {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}
.detail-row .label {
  color: #94a3b8;
  font-weight: 500;
  min-width: 5rem;
  flex-shrink: 0;
}
.detail-row .value {
  flex: 1;
  color: #fff;
  word-break: break-all;
}
.raw-data-toggle {
  margin-top: 0.75rem;
  text-align: center;
}
.toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  border: 1px solid #475569;
  border-radius: 9999px;
  padding: 0.4rem 1rem;
  color: #93c5fd;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.toggle-btn:hover { background: #3c4a60; }
.toggle-btn.active { background: #3c4a60; border-color: #93c5fd; }
.toggle-icon { transition: transform 0.2s ease; }
.toggle-btn.active .toggle-icon { transform: rotate(180deg); }
.raw-details-wrapper {
  position: relative;
  margin-top: 0.75rem;
  background: #151d27;
  border-radius: 0.5rem;
  border: 1px solid #3c4a60;
  overflow: hidden;
}
.raw-details {
  padding: 1rem;
  font-size: 0.75rem;
  color: #e2e8f0;
  white-space: pre-wrap;
  word-break: break-all;
  overflow: auto;
  max-height: 200px;
  line-height: 1.5;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
  margin: 0;
}
.copy-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(147, 197, 253, 0.2);
  border: none;
  border-radius: 0.25rem;
  padding: 0.5rem;
  color: #93c5fd;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
}
.copy-btn:hover {
  background: rgba(147, 197, 253, 0.4);
}

/* 确保跨平台字体一致性 */
* {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 移除浏览器默认的outline */
button:focus {
  outline: none;
}

/* 确保在不同分辨率下的一致显示 */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .threat-level-badge,
  .risk-score-badge,
  .threat-badge {
    -webkit-font-smoothing: subpixel-antialiased;
  }
}
</style>