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
      searchResults: [],
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
    // 并行加载数据以提高速度
    console.log('Dashboard mounted, starting data loading...')
    
    // 先加载搜索历史（同步操作）
    this.loadSearchHistory()
    
    // 并行加载CVE和新闻数据
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
        console.log('Loading CVE data...')
        const startTime = performance.now()
        
        const response = await getAllCVE()
        
        const endTime = performance.now()
        console.log(`CVE API call took ${endTime - startTime} milliseconds`)
        console.log('CVE API Response:', response)
        
        if (Array.isArray(response)) {
          this.cveData = response
          console.log(`CVE Data loaded successfully: ${this.cveData.length} items`)
        } else {
          console.error('CVE API response is not an array:', response)
          this.cveData = []
        }
      } catch (error) {
        console.error('Failed to load CVE data:', error)
        this.cveData = []
        
        // 显示用户友好的错误信息
        this.$toast?.error?.('CVE数据加载失败，请稍后重试')
      } finally {
        this.cveLoading = false
      }
    },

    async loadNewsData() {
      if (this.newsLoading) return
      
      this.newsLoading = true
      try {
        console.log('Loading news data...')
        const startTime = performance.now()
        
        // 添加重试逻辑
        let response = null
        let retryCount = 0
        const maxRetries = 3
        
        while (retryCount < maxRetries && !response) {
          try {
            if (retryCount > 0) {
              console.log(`News API retry attempt ${retryCount}`)
              await new Promise(resolve => setTimeout(resolve, 1000 * retryCount))
            }
            
            response = await getNewsData()
            break
          } catch (error) {
            retryCount++
            console.warn(`News API attempt ${retryCount} failed:`, error.message)
            
            if (retryCount === maxRetries) {
              throw error
            }
          }
        }
        
        const endTime = performance.now()
        console.log(`News API call took ${endTime - startTime} milliseconds`)
        console.log('News API Response:', response)
        console.log('Response type:', typeof response)
        console.log('Is array:', Array.isArray(response))
        
        if (Array.isArray(response)) {
          this.newsData = response
          console.log(`News Data loaded successfully: ${this.newsData.length} items`)
        } else if (response === undefined || response === null) {
          console.error('News API returned undefined/null')
          this.newsData = []
          throw new Error('News API returned no data')
        } else {
          console.error('News API response is not an array:', response)
          this.newsData = []
        }
        
      } catch (error) {
        console.error('Failed to load news data:', error)
        console.error('Error details:', {
          message: error.message,
          stack: error.stack,
          name: error.name
        })
        this.newsData = []
        
        // 显示用户友好的错误信息
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

        const newSearch = { query, type, timestamp: Date.now() }
        this.searchHistory = [newSearch, ...this.searchHistory.filter(h => h.query !== query)]
        this.searchHistory = this.searchHistory.slice(0, 10)
        this.saveSearchHistory()
      } catch (error) {
        console.error('Search failed:', error)
        this.searchResults = []
        this.$toast?.error?.('搜索失败，请重试')
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
          console.log('Search history loaded:', this.searchHistory.length, 'items')
        }
      } catch (error) {
        console.warn('localStorage not available, starting with empty history')
        this.searchHistory = []
      }
    },

    // 手动刷新所有数据
    async refreshAllData() {
      console.log('Manual refresh triggered')
      await Promise.allSettled([
        this.loadCveData(),
        this.loadNewsData()
      ])
    }
  },

  // 监听数据变化
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
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
}


.content-grid {
  /* 确保始终为三列布局，完全适应屏幕 */
  display: grid;
  grid-template-columns: 0.7fr 1.2fr 0.7fr;
  gap: 0.5rem;
  min-height: 600px;
  width: 100%;
  box-sizing: border-box;
}

/* 确保各个区域有合适的高度 */
.cve-section,
.news-section {
  min-height: 600px;
}

.search-section {
  min-height: 400px;
}

/* 移除所有媒体查询，以禁用响应式布局 */

/* 添加一些过渡动画 */
.cve-section,
.news-section,
.search-section {
  transition: all 0.3s ease;
}
</style>