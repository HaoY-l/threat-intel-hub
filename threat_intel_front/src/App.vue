<template>
  <div id="app">
    <!-- 登录状态判断：未登录显示登录页，已登录显示功能页 -->
    <template v-if="isLoggedIn">
      <!-- 已登录：显示导航栏 + 功能页面 -->
      <Header :active="activeTab" @tab-change="handleTabChange" />
      <component :is="activeView" style="flex-grow: 1;" />
    </template>
    <template v-else>
      <!-- 未登录：显示登录页 -->
      <Login @login-success="handleLoginSuccess" />
    </template>
  </div>
</template>

<script>
// 导入原有组件
import Header from './components/common/Header.vue'
import Dashboard from './views/Dashboard.vue'
import Tools from './views/Tools.vue'
import WAFManagement from './views/WAFManagement.vue'
import PhishingEmail from './views/PhishingEmail.vue'
// 导入登录页组件（之前提供的 Login.vue）
import Login from './views/Login.vue'
// 导入权限工具函数
import { isLoggedIn, getCurrentUser, logout as authLogout } from './utils/auth'

export default {
  name: 'App',
  components: {
    Header,
    Dashboard,
    Tools,
    WAFManagement,
    PhishingEmail,
    Login // 注册登录页组件
  },
  data() {
    return {
      activeTab: 'threat', // 强制默认：威胁情报（所有用户统一）
      isLoggedIn: false // 登录状态标记
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
    // 根据用户角色控制导航栏菜单显示（可选，增强权限控制）
    isAdmin() {
      const user = getCurrentUser()
      return user && user.role === 'admin'
    }
  },
  created() {
    // 页面初始化时：1. 检查登录状态 2. 读取本地存储的当前页面（优先级：缓存 > 默认）
    this.checkLoginStatus()
    this.initActiveTabFromStorage()
  },
  methods: {
    // 初始化当前页面：优先读取本地存储（切换过标签才会有缓存），无则用默认值（threat）
    initActiveTabFromStorage() {
      const savedTab = localStorage.getItem('activeTab')
      // 合法标签列表（防止缓存无效值）
      const validTabs = ['threat', 'waf', 'phishing', 'tools']
      // 只有缓存存在时才覆盖默认值（首次登录无缓存，仍显示威胁情报）
      if (validTabs.includes(savedTab)) {
        this.activeTab = savedTab
      } else {
        // 无有效缓存：强制默认威胁情报（不管是否管理员）
        this.activeTab = 'threat'
        // 写入默认值到本地存储（避免重复判断）
        localStorage.setItem('activeTab', 'threat')
      }
    },
    // 检查登录状态（从本地存储读取）
    checkLoginStatus() {
      this.isLoggedIn = isLoggedIn()
    },
    // 处理标签切换：更新状态 + 存入本地存储
    handleTabChange(tab) {
      const validTabs = ['threat', 'waf', 'phishing', 'tools']
      if (validTabs.includes(tab)) {
        this.activeTab = tab
        localStorage.setItem('activeTab', tab) // 切换时存入缓存，刷新后保持
      }
    },
    // 登录成功回调（接收登录页传递的用户信息）
    handleLoginSuccess(userInfo) {
      this.isLoggedIn = true
      // 登录后初始化页面：强制默认威胁情报（覆盖管理员之前的默认waf逻辑）
      this.$nextTick(() => {
        this.activeTab = 'threat'
        localStorage.setItem('activeTab', 'threat')
        // 登录成功提示
        this.$message.success(`欢迎回来，${userInfo.username}！`)
      })
    },
    // 注销登录（导航栏调用此方法）
    logout() {
      authLogout() // 调用auth工具的注销方法
      this.isLoggedIn = false
      this.activeTab = 'threat'
      localStorage.removeItem('activeTab') // 注销时清除缓存，下次登录仍默认威胁情报
      this.$message.success('已成功注销')
    }
  }
}
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background-color: #0f0f23;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 确保根 HTML 和 Body 元素占满全屏 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}

/* 登录页容器样式（与深色主题适配） */
.login-container {
  background-color: #0f0f23;
}

/* 功能页面内容区样式（避免紧贴导航栏） */
.component {
  padding: 1.5rem;
}
</style>