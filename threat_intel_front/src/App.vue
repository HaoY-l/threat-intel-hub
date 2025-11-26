<template>
  <div id="app">
    <!-- 登录状态判断：未登录显示登录页，已登录显示功能页 -->
    <template v-if="isLoggedIn && permissionsLoaded"> <!-- 新增：权限加载完成才渲染功能页 -->
      <Header :active="activeTab" @tab-change="handleTabChange" />
      <component :is="activeView" style="flex-grow: 1;" />
    </template>
    <template v-else-if="!isLoggedIn">
      <Login @login-success="handleLoginSuccess" />
    </template>
    <template v-else>
      <!-- 权限加载中：显示加载提示 -->
      <div class="loading-container" v-loading="true" element-loading-text="权限加载中...">
        <!-- 使用 v-loading 指令代替 el-loading-spinner 组件 -->
      </div>
    </template>
  </div>
</template>

<script>
import Header from './components/common/Header.vue'
import Dashboard from './views/Dashboard.vue'
import Tools from './views/Tools.vue'
import WAFManagement from './views/WAFManagement.vue'
import PhishingEmail from './views/PhishingEmail.vue'
import Login from './views/Login.vue'
import { isLoggedIn, getCurrentUser, logout as authLogout } from './utils/auth'
import { usePermission } from './utils/permission'

export default {
  name: 'App',
  components: {
    Header,
    Dashboard,
    Tools,
    WAFManagement,
    PhishingEmail,
    Login
  },
  data() {
    return {
      activeTab: 'threat',
      isLoggedIn: false,
      permissionsLoaded: false // 新增：权限加载状态标记
    }
  },
  computed: {
    activeView() {
      switch (this.activeTab) {
        case 'tools':
          return 'Tools'
        case 'waf':
          return 'WAFManagement'
        case 'phishing': 
          return 'PhishingEmail'
        case 'threat':
        default:
          return 'Dashboard'
      }
    },
    isAdmin() {
      const user = getCurrentUser()
      return user && user.role === 'admin'
    }
  },
  created() {
    this.checkLoginStatus()
    this.initActiveTabFromStorage()
    // 已登录时，初始化权限（页面刷新场景）
    if (this.isLoggedIn) {
      this.initUserPermissions()
    }
  },
  methods: {
    // 初始化权限（封装为独立方法）
    async initUserPermissions() {
      try {
        const { initUserPermissions } = usePermission()
        await initUserPermissions() // 等待权限加载完成
        this.permissionsLoaded = true // 标记权限加载完成
      } catch (error) {
        console.error('权限初始化失败：', error)
        this.$message.warning('权限初始化失败，部分功能可能无法正常使用')
        this.permissionsLoaded = true // 即使失败，也允许页面渲染
      }
    },
    initActiveTabFromStorage() {
      const savedTab = localStorage.getItem('activeTab')
      const validTabs = ['threat', 'waf', 'phishing', 'tools']
      if (validTabs.includes(savedTab)) {
        this.activeTab = savedTab
      } else {
        this.activeTab = 'threat'
        localStorage.setItem('activeTab', 'threat')
      }
    },
    checkLoginStatus() {
      this.isLoggedIn = isLoggedIn()
    },
    handleTabChange(tab) {
      const validTabs = ['threat', 'waf', 'phishing', 'tools']
      if (validTabs.includes(tab)) {
        this.activeTab = tab
        localStorage.setItem('activeTab', tab)
      }
    },
    // 登录成功回调：先初始化权限，再更新状态
    async handleLoginSuccess(userInfo) {
      this.isLoggedIn = true
      await this.initUserPermissions() // 关键：等待权限加载完成
      this.$nextTick(() => {
        this.activeTab = 'threat'
        localStorage.setItem('activeTab', 'threat')
        this.$message.success(`欢迎回来，${userInfo.username}！`)
      })
    },
    logout() {
      authLogout()
      this.isLoggedIn = false
      this.permissionsLoaded = false // 重置权限加载状态
      this.activeTab = 'threat'
      localStorage.removeItem('activeTab')
      this.$message.success('已成功注销')
    }
  }
}
</script>

<style>
/* 加载提示样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #0f0f23;
}

/* 自定义 loading 样式 */
::v-deep(.el-loading-mask) {
  background-color: rgba(15, 15, 35, 0.9) !important;
}

::v-deep(.el-loading-spinner .circular) {
  width: 60px !important;
  height: 60px !important;
}

::v-deep(.el-loading-text) {
  color: #e0e0e0 !important;
  font-size: 16px !important;
  margin-top: 20px !important;
}

/* 原有样式保持不变 */
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background-color: #0f0f23;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}
.login-container {
  background-color: #0f0f23;
}
.component {
  padding: 1.5rem;
}
</style>