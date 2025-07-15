<template>
  <div id="app">
    <!-- 传入 activeTab 给 Header，让导航按钮高亮 -->
    <Header :active="activeTab" @tab-change="activeTab = $event" />

    <!-- 根据 activeTab 渲染对应的页面 -->
    <component :is="activeView" />
  </div>
</template>

<script>
import Header from './components/common/Header.vue'
import Dashboard from './views/Dashboard.vue'
import Settings from './views/Settings.vue'
import WAFManagement from './views/WAFManagement.vue'

export default {
  name: 'App',
  components: {
    Header,
    Dashboard,
    Settings,
    WAFManagement
  },
  data() {
    return {
      activeTab: 'threat' // 默认页面：威胁情报
    }
  },
  computed: {
    activeView() {
      switch (this.activeTab) {
        case 'settings':
          return 'Settings'
        case 'waf':
          return 'WAFManagement'
        case 'threat':
        default:
          return 'Dashboard'
      }
    }
  }
}
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background-color: #0f0f23;
  min-height: 100vh;
}
</style>
