// ✅ Dashboard.vue
<template>
  <div class="dashboard">
    <Header />

    <main class="main-content">
      <div class="container">
        <div class="content-grid">
          <div class="cve-section">
            <CVEList :cve-data="cveData" />
          </div>

          <div class="search-section">
            <SearchPanel 
              @search="handleSearch"
              @tab-change="handleTabChange"
              :loading="loading"
            />

            <SearchResults 
              v-if="searchDialogVisible"
              :visible="searchDialogVisible"
              :threatData="searchDialogData"
              @close="searchDialogVisible = false"
            />

            <SearchHistory 
              v-if="searchHistory.length > 0"
              :history="searchHistory"
              @search-again="handleSearchAgain"
            />
          </div>
        </div>
      </div>
    </main>

    <AppFooter />
  </div>
</template>

<script>
import Header from '../components/common/Header.vue'
import AppFooter from '../components/common/AppFooter.vue'
import CVEList from '../components/cve/CVEList.vue'
import SearchPanel from '../components/search/SearchPanel.vue'
import SearchResults from '../components/search/SearchResults.vue'
import SearchHistory from '../components/search/SearchHistory.vue'
import { getAllCVE, queryThreatIntel } from '../utils/api.js'

export default {
  name: 'Dashboard',
  components: {
    Header,
    AppFooter,
    CVEList,
    SearchPanel,
    SearchResults,
    SearchHistory
  },
  data() {
    return {
      cveData: [],
      searchResults: [],
      searchHistory: [],
      activeSearchType: 'ip',
      searchDialogVisible: false,
      searchDialogData: null,
      loading: false
    }
  },
  async mounted() {
    await this.loadCVEData()
    this.loadSearchHistory()
  },
  methods: {
    async loadCVEData() {
      try {
        this.cveData = await getAllCVE()
      } catch (error) {
        console.error('Failed to load CVE data:', error)
      }
    },

    async handleSearch({ query, type }) {
      if (!query.trim()) return

      this.loading = true
      this.activeSearchType = type

      try {
        const results = await queryThreatIntel(query, type)

        // 弹窗展示结果
        this.searchDialogVisible = true
        this.searchDialogData = results

        const detailResults = Object.values(results.results || {})
        const scores = detailResults.map(r => typeof r.reputation_score === 'number' ? r.reputation_score : 0)
        const levels = detailResults.map(r => r.threat_level || '')
        const minScore = Math.min(...scores)
        const maxLevel = levels.includes('high') || levels.includes('malicious')
          ? 'malicious'
          : levels.includes('medium') || levels.includes('suspicious')
          ? 'suspicious'
          : levels.includes('low') || levels.includes('harmless')
          ? 'harmless'
          : 'unknown'

        const historyItem = {
          id: Date.now(),
          query,
          type,
          timestamp: new Date().toISOString(),
          results: detailResults.length,
          detailResults: detailResults.map(({ details, ...rest }) => rest),
          maxScore: minScore,
          maxThreatLevel: maxLevel
        }

        this.searchResults = detailResults
        this.searchHistory.unshift(historyItem)
        this.searchHistory = this.searchHistory.slice(0, 10)
        this.saveSearchHistory()
      } catch (error) {
        console.error('Search failed:', error)
        this.searchResults = []
      } finally {
        this.loading = false
      }
    },

    handleTabChange(type) {
      this.activeSearchType = type
    },

    handleSearchAgain({ query, type }) {
      this.handleSearch({ query, type })
    },

    saveSearchHistory() {
      localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory))
    },

    loadSearchHistory() {
      const saved = localStorage.getItem('searchHistory')
      if (saved) {
        this.searchHistory = JSON.parse(saved)
      }
    }
  }
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f23 0%, #1a0033 50%, #0f0f23 100%);
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 2rem 0;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  align-items: start;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

.cve-section,
.search-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>