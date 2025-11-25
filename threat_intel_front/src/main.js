import { createApp } from 'vue'
import App from './App.vue'
import './assets/styles/global.css'
// 引入 Element Plus（用于登录页组件、消息提示，若未安装需执行 npm install element-plus @element-plus/icons-vue）
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 引入封装的请求工具（之前提供的 request.js）
import request from './utils/request'
// 引入权限工具函数（之前提供的 auth.js）
import * as auth from './utils/auth'

const app = createApp(App)

// 全局挂载依赖（方便组件内使用）
app.use(ElementPlus)
app.config.globalProperties.$request = request // 全局请求工具
app.config.globalProperties.$auth = auth // 全局权限工具

app.mount('#app')