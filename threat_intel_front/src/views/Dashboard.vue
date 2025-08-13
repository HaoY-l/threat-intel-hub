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

          <div class="news-section">
            <NewsPanel 
              :news-data="newsData"
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
      searchResults: [],
      searchHistory: [],
      newsData: [],
      activeSearchType: 'ip',
      searchDialogVisible: false,
      searchDialogData: null,
      loading: false
    }
  },
  async mounted() {
    await this.loadCveData()
    await this.loadNewsData()
    this.loadSearchHistory()
  },
  methods: {
    async loadCveData() {
      try {
        const response = await getAllCVE()
        console.log('CVE API Response:', response)
        
        // 现在两个接口都直接返回数组，统一处理
        if (Array.isArray(response)) {
          this.cveData = response
        } else {
          console.error('CVE API response is not an array:', response)
          this.cveData = []
        }
        
        console.log('CVE Data loaded:', this.cveData.length, 'items')
      } catch (error) {
        console.error('Failed to load CVE data:', error)
        this.cveData = []
      }
    },

    async loadNewsData() {
      try {
        console.log('Starting to load news data...')
        
        // 临时直接测试API调用
        const testResponse = await fetch('/api/news')
        const testData = await testResponse.json()
        console.log('Direct fetch test:', testData)
        
        const response = await getNewsData()
        console.log('getNewsData result:', response)
        console.log('Response type:', typeof response)
        console.log('Is array:', Array.isArray(response))
        
        // 现在News接口也直接返回数组，与CVE接口格式一致
        if (Array.isArray(response)) {
          this.newsData = response
        } else if (response === undefined || response === null) {
          console.error('News API returned undefined/null - check getNewsData function')
          this.newsData = []
        } else {
          console.error('News API response is not an array:', response)
          this.newsData = []
        }
        
        console.log('News Data loaded:', this.newsData.length, 'items')
      } catch (error) {
        console.error('Failed to load news data:', error)
        console.error('Error details:', error.message, error.stack)
        this.newsData = []
      }
    },

    async handleSearch({ query, type }) {
      this.loading = true
      try {
        const threatData = await queryThreatIntel(query, type)
        this.searchDialogData = threatData
        this.searchDialogVisible = true

        const newSearch = { query, type, timestamp: Date.now() }
        this.searchHistory = [newSearch, ...this.searchHistory.filter(h => h.query !== query)]
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
      // 注意：在Claude.ai环境中不能使用localStorage
      // 如果需要持久化存储，建议使用内存存储或发送到服务器
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
    }
  }
}
</script>

<style scoped>
/* 样式部分保持不变 */
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
  grid-template-columns: 1fr 1.5fr 1fr;
  gap: 2rem;
}

@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }

  .cve-section,
  .news-section {
    grid-row: 2;
  }

  .search-section {
    grid-row: 1;
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .cve-section,
  .news-section {
    grid-row: auto;
  }

  .search-section {
    grid-row: auto;
    grid-column: auto;
  }
}
</style>