<template>
  <div class="cve-list">
    <div class="list-header">
      <h2>
        <i class="fas fa-exclamation-triangle"></i>
        最新CVE漏洞
      </h2>
      <div class="count">{{ cveData.length }} 条记录</div>
    </div>
    
    <div class="cve-items">
      <CVECard 
        v-for="cve in cveData" 
        :key="cve.id"
        :cve="cve"
        @click="handleCVEClick"
      />
    </div>
  </div>
</template>

<script>
import CVECard from './CVECard.vue'

export default {
  name: 'CVEList',
  components: {
    CVECard
  },
  props: {
    cveData: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    handleCVEClick(cve) {
      if (cve.url) {
        window.open(cve.url, '_blank')
      }
    }
  }
}
</script>

<style scoped>
.cve-list {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 1rem;
  padding: 1.5rem;
  height: fit-content;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
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
  color: #ef4444;
}

.count {
  font-size: 0.875rem;
  color: #a855f7;
}

.cve-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 38rem;
  overflow-y: auto;
}

.cve-items::-webkit-scrollbar {
  width: 4px;
}

.cve-items::-webkit-scrollbar-track {
  background: rgba(30, 41, 59, 0.5);
  border-radius: 2px;
}

.cve-items::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.5);
  border-radius: 2px;
}

.cve-items::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.7);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .cve-list {
    padding: 1rem;
  }
  
  .list-header {
    margin-bottom: 1rem;
  }
}
</style>