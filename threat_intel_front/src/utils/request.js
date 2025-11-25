import axios from 'axios';
import { ElMessage } from 'element-plus';
import { isLoggedIn, logout, getCurrentUser } from './auth';

// 1. 彻底删除 Vue Router 相关代码（useRouter 和 router 实例）

// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8891', // 后端基础地址（默认localhost:8891，适配你的后端端口）
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json' // 统一请求格式
  }
});

// 请求拦截器：添加登录状态校验（未登录直接终止请求）
service.interceptors.request.use(
  (config) => {
    // 检查是否已登录（未登录则提示并终止请求）
    if (!isLoggedIn()) {
      ElMessage.warning('请先登录后再操作');
      return Promise.reject(new Error('未登录，请求终止'));
    }

    // 若后续改用JWT，需添加以下代码（当前用session无需）：
    // const user = getCurrentUser();
    // if (user && user.token) {
    //   config.headers.Authorization = `Bearer ${user.token}`;
    // }

    return config;
  },
  (error) => {
    ElMessage.error('请求发送失败，请重试');
    return Promise.reject(error);
  }
);

// 响应拦截器：处理错误状态码（无路由适配）
service.interceptors.response.use(
  (response) => response.data, // 直接返回响应体（简化前端调用）
  (error) => {
    const status = error.response?.status;
    switch (status) {
      // 401：未登录或会话过期 → 注销+刷新页面（App.vue自动显示登录页）
      case 401:
        ElMessage.error('登录状态已失效，请重新登录');
        logout(); // 清除本地存储
        window.location.reload(); // 刷新页面，触发App.vue的登录状态检查
        break;
      // 403：无权限访问 → 仅提示，不跳转（无路由）
      case 403:
        ElMessage.error('您没有权限执行该操作');
        break;
      // 其他错误：统一提示后端返回的消息
      default:
        ElMessage.error(error.response?.data?.message || '请求失败，请重试');
    }
    return Promise.reject(error);
  }
);

export default service;