// ✅ Dashboard.vue
<template>
  <div class="dashboard">
    <main class="main-content">
      <div class="container">
        <div class="content-grid">
          <!-- CVE 区域 -->
          <div class="cve-section">
            <CVEList :cve-data="cveData" />
          </div>

          <!-- 查询区域 -->
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

          <!-- 新闻区域 -->
          <div class="news-section">
            <NewsPanel :news-data="newsData" />
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
import { getAllCVE, queryThreatIntel } from '../utils/api.js'

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
    await this.loadCVEData()
    this.loadSearchHistory()
    await this.loadNewsData()
  },
  methods: {
    async loadCVEData() {
      try {
        this.cveData = await getAllCVE()
      } catch (error) {
        console.error('Failed to load CVE data:', error)
      }
    },

    async loadNewsData() {
      // 🔄 TODO: 替换为真实的新闻API调用
      // 可选的免费威胁情报新闻API：
      // 1. MISP项目 - https://www.misp-project.org/
      // 2. PhishTank - https://phishtank.org/
      // 3. SecurityWeek RSS - https://www.securityweek.com/
      // 4. FreeBuf RSS - https://www.freebuf.com/
      
      // 当前使用模拟数据，实际项目中请替换为：
      // this.newsData = await getSecurityNews()
      
      this.newsData = [
        {
          id: 1,
          title: "新型APT组织利用0day漏洞攻击关键基础设施",
          summary: "安全研究人员发现一个新的APT组织正在利用未修补的0day漏洞...",
          source: "FreeBuf",
          time: "2小时前",
          category: "APT攻击",
          severity: "高危"
        },
        {
          id: 2,
          title: "ChatGPT遭遇大规模数据泄露事件",
          summary: "OpenAI确认部分用户对话记录可能被未授权访问...",
          source: "安全内参",
          time: "4小时前", 
          category: "数据泄露",
          severity: "中危"
        },
        {
          id: 3,
          title: "勒索软件Lockbit3.0变种分析报告",
          summary: "研究团队深入分析了Lockbit3.0的最新变种，发现其加密算法...",
          source: "奇安信威胁情报中心",
          time: "6小时前",
          category: "恶意软件",
          severity: "高危"
        },
        {
          id: 4,
          title: "工控系统漏洞CVE-2025-1234影响全球制造业",
          summary: "新发现的工控系统漏洞可能影响数千家制造企业...",
          source: "工控安全",
          time: "8小时前",
          category: "工控安全",
          severity: "严重"
        },
        {
          id: 5,
          title: "国家级黑客组织针对金融机构发起钓鱼攻击",
          summary: "多家银行收到针对性钓鱼邮件，攻击手法极其隐蔽...",
          source: "金融安全",
          time: "10小时前",
          category: "钓鱼攻击",
          severity: "高危"
        }
      ]
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
  grid-template-columns: 1fr 1.5fr 1fr;
  gap: 1.5rem;
  align-items: start;
}

@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }
  
  .news-section {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

.cve-section,
.search-section,
.news-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>