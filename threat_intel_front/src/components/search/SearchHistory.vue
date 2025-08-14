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
            <i :class="getTypeIcon(item.type)"></i>
            <code class="history-query" :title="item.query">{{ item.query }}</code>
            <span class="result-count">{{ item.results || 0 }} 结果</span>
            <span 
              v-if="item.maxThreatLevel"
              class="threat-level"
              :class="getThreatLevelClass(item.maxThreatLevel)"
            >
              {{ getThreatLevelText(item.maxThreatLevel) }}
            </span>
            <span 
              v-if="item.maxScore !== undefined"
              class="max-score"
              :class="getScoreClass(item.maxScore)"
            >
              风险: {{ item.maxScore }}
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
    getScoreClass(score){ const s=parseInt(score)||0; if(s>70) return'score-high';if(s>30)return'score-medium';return'score-low'; },
    getDisplayId(result,type){return type==='url'?result.target_url||result.id:result.id;},
    formatTime(ts){return new Date(ts).toLocaleString('zh-CN');},
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
/* 外部历史卡片保持不变 */
.search-history { background: rgba(30,41,59,0.95); border-radius:1rem; padding:1rem; color:#f3f4f6; max-height:100vh; overflow:hidden; }
.history-header { display:flex; align-items:center; gap:0.5rem; font-size:1rem; font-weight:500; margin-bottom:1rem; }
.history-header i { color:#8b5cf6; }
.history-list { display:flex; flex-direction:column; gap:0.5rem; max-height:calc(100vh - 6rem); overflow-y:auto; padding-right:0.25rem; }
.history-item { background: rgba(0,0,0,0.6); border-radius:0.5rem; transition:all 0.2s ease; padding:0.5rem; }
.history-item:hover { background: rgba(0,0,0,0.75); }
.history-item.expanded { background: rgba(30,41,59,0.95); }
.history-content { display:flex; align-items:center; justify-content:space-between; cursor:pointer; }
.history-info { display:flex; align-items:center; gap:0.5rem; flex:1; }
.history-info i { color:#8b5cf6; width:1rem; }
.history-query, .hash-value, .url-value { font-family:'Courier New',monospace; font-size:0.7rem; color:#ffffff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:200px; }
.result-count { color:#a855f7; font-size:0.7rem; }
.threat-level,.max-score{font-size:0.7rem;font-weight:500;padding:0.15rem 0.3rem;border-radius:0.25rem;white-space:nowrap;}
.threat-malicious{color:#fff;background:rgba(239,68,68,0.85);}
.threat-suspicious{color:#fff;background:rgba(249,115,22,0.85);}
.threat-harmless{color:#fff;background:rgba(34,197,94,0.85);}
.threat-unknown{color:#fff;background:rgba(107,114,128,0.85);}
.score-high{color:#fff;background:rgba(239,68,68,0.85);}
.score-medium{color:#fff;background:rgba(249,115,22,0.85);}
.score-low{color:#fff;background:rgba(34,197,94,0.85);}
.history-actions { display:flex; align-items:center; gap:0.5rem; }
.history-time { color:#d1d5db; font-size:0.65rem; }
.action-btn { background: rgba(71,85,105,0.3); border:1px solid rgba(139,92,246,0.3); border-radius:0.25rem; padding:0.25rem 0.4rem; color:#a855f7; cursor:pointer; font-size:0.65rem; transition:all 0.2s ease;}
.action-btn:hover { background: rgba(139,92,246,0.3); border-color: rgba(139,92,246,0.7);}
.expand-btn i.rotated{transform:rotate(180deg);}

/* --- 新的详情卡片样式 --- */

/* 详情容器 */
.history-details-container {
  padding: 0.75rem 0.5rem 0 0.5rem; /* 调整内边距 */
  border-top: 1px solid rgba(147, 197, 253, 0.1); /* 柔和的边框 */
  margin-top: 0.5rem;
}

/* 统计条 */
.details-stats-bar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 0.75rem;
  font-size: 0.8rem;
  color: #94a3b8; /* 柔和的文字颜色 */
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(147, 197, 253, 0.1);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 结果列表 */
.results-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* 结果项卡片 */
.result-item {
  background: #1e293b; /* 更深的背景色 */
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #3c4a60; /* 柔和的边框 */
  transition: all 0.2s ease;
}

/* 结果头部 */
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
  font-size: 0.8rem;
  font-weight: 500;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  color: #fff;
  white-space: nowrap;
}
.threat-malicious { background: #ef4444; }
.threat-suspicious { background: #f97316; }
.threat-harmless { background: #22c55e; }
.threat-unknown { background: #64748b; }

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

/* 详细信息行 */
.result-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.8rem;
}
.detail-row {
  display: flex;
  gap: 0.5rem;
}
.detail-row .label {
  color: #94a3b8;
  font-weight: 500;
  min-width: 5rem;
}
.detail-row .value {
  flex: 1;
  color: #fff;
  word-break: break-all;
}

/* 原始数据部分 */
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
</style>