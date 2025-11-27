import { createApp } from 'vue'
import App from './App.vue'
import './assets/styles/global.css'
// 引入 Element Plus 及图标（用户管理组件需要）
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue' // 引入所有图标
// 引入封装的请求工具
import request from './utils/request'
// 引入权限工具函数
import * as auth from './utils/auth'

const app = createApp(App)

// 全局注册 Element Plus 图标（用户管理组件需要用到el-icon）
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 全局挂载依赖
app.use(ElementPlus)
app.config.globalProperties.$request = request // 全局请求工具
app.config.globalProperties.$auth = auth // 全局权限工具

// 全局注入request（用户管理组件可通过inject获取）
app.provide('request', request)

app.mount('#app')