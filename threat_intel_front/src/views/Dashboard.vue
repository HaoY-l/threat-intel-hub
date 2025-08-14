<template>
  <div class="dashboard">
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
              ref="searchPanel"
            />

            <SearchResults 
              v-if="searchDialogVisible"
              :visible="searchDialogVisible"
              :threatData="searchDialogData"
              @close="searchDialogVisible = false"
              @copy-success="showCopySuccess"
            />

            <SearchHistory 
              v-if="searchHistory.length > 0"
              :history="searchHistory"
              @search-again="handleSearchAgain"
            />
          </div>

          <div class="news-section">
            <NewsPanel 
              :news-data="newsData"
              :is-loading="newsLoading"
              @refresh="loadNewsData"
            />
          </div>
        </div>
      </div>
    </main>

    <AppFooter />
  </div>
</template>

<script>
import AppFooter from '../components/common/AppFooter.vue'
import CVEList from '../components/cve/CVEList.vue'
import SearchPanel from '../components/search/SearchPanel.vue'
import SearchResults from '../components/search/SearchResults.vue'
import SearchHistory from '../components/search/SearchHistory.vue'
import NewsPanel from '../components/news/NewsPanel.vue'
import { getAllCVE, queryThreatIntel, getNewsData } from '../utils/api.js'

export default {
  name: 'Dashboard',
  components: {
    AppFooter,
    CVEList,
    SearchPanel,
    SearchResults,
    SearchHistory,
    NewsPanel
  },
  data() {
    return {
      cveData: [],
      searchHistory: [],
      newsData: [],
      activeSearchType: 'ip',
      searchDialogVisible: false,
      searchDialogData: null,
      loading: false,
      newsLoading: false,
      cveLoading: false
    }
  },
  async mounted() {
    console.log('Dashboard mounted, starting data loading...')
    this.loadSearchHistory()
    
    const loadPromises = [
      this.loadCveData(),
      this.loadNewsData()
    ]
    
    try {
      await Promise.allSettled(loadPromises)
      console.log('All data loading completed')
    } catch (error) {
      console.error('Error during data loading:', error)
    }
  },
  methods: {
    async loadCveData() {
      if (this.cveLoading) return
      this.cveLoading = true
      try {
        const response = await getAllCVE()
        if (Array.isArray(response)) {
          this.cveData = response
        } else {
          console.error('CVE API response is not an array:', response)
          this.cveData = []
        }
      } catch (error) {
        console.error('Failed to load CVE data:', error)
        this.cveData = []
        this.$toast?.error?.('CVE数据加载失败，请稍后重试')
      } finally {
        this.cveLoading = false
      }
    },

    async loadNewsData() {
      if (this.newsLoading) return
      this.newsLoading = true
      try {
        let response = await getNewsData()
        if (Array.isArray(response)) {
          this.newsData = response
        } else {
          console.error('News API response is not an array:', response)
          this.newsData = []
        }
      } catch (error) {
        console.error('Failed to load news data:', error)
        this.newsData = []
        this.$toast?.error?.('新闻数据加载失败，请稍后重试')
      } finally {
        this.newsLoading = false
      }
    },

    async handleSearch({ query, type }) {
      this.loading = true
      try {
        const threatData = await queryThreatIntel(query, type)
        this.searchDialogData = threatData
        this.searchDialogVisible = true

        const newSearch = { 
          query, 
          type, 
          timestamp: Date.now(),
          results: Object.keys(threatData.results || {}).length,
          detailResults: Object.values(threatData.results || {}).map(r => ({...r, id: r.id || query}))
        }
        this.searchHistory = [newSearch, ...this.searchHistory.filter(h => !(h.query === query && h.type === type))]
        if (this.searchHistory.length > 10) {
          this.searchHistory = this.searchHistory.slice(0, 10)
        }
        this.saveSearchHistory()
      } catch (error) {
        console.error('Search failed:', error)
        this.$toast?.error?.('搜索失败，请重试')
      } finally {
        this.loading = false
      }
    },
    
    handleSearchAgain({ query, type }) {
      this.$refs.searchPanel.setSearchQuery(query, type)
      this.handleSearch({ query, type })
    },
    
    handleTabChange(type) {
      this.activeSearchType = type
    },

    saveSearchHistory() {
      try {
        localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory))
      } catch (error) {
        console.warn('localStorage not available, using memory storage only')
      }
    },

    loadSearchHistory() {
      try {
        const saved = localStorage.getItem('searchHistory')
        if (saved) {
          this.searchHistory = JSON.parse(saved)
        }
      } catch (error) {
        console.warn('localStorage not available, starting with empty history')
        this.searchHistory = []
      }
    },

    showCopySuccess() {
      this.$toast?.success?.('已成功复制到剪贴板')
    },

    async refreshAllData() {
      await Promise.allSettled([
        this.loadCveData(),
        this.loadNewsData()
      ])
    }
  },
  watch: {
    newsData: {
      handler(newVal) {
        console.log('NewsData watcher triggered:', newVal?.length || 0, 'items')
      },
      immediate: true
    },
    cveData: {
      handler(newVal) {
        console.log('CVEData watcher triggered:', newVal?.length || 0, 'items')
      },
      immediate: true
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
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 1.5rem;
  box-sizing: border-box;
  width: 100%;
}

.content-grid {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr 0.8fr;
  gap: 1.5rem;
  width: 100%;
}

.cve-section,
.news-section,
.search-section {
  min-height: 400px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 1rem 0;
  }
  .container {
    padding: 0 1rem;
  }
  .content-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
</style>