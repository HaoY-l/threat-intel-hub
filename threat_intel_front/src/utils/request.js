import axios from 'axios';
import { ElMessage } from 'element-plus';
import { isLoggedIn, logout, getCurrentUser } from './auth';

// 创建 Axios 实例（适配 Session 认证）
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8891', // 后端地址（与 Flask 端口一致）
  timeout: 8000, // 延长超时时间（避免数据库操作超时）
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true, // 核心：允许跨域携带 Cookie（Session 认证必需）
});

// 请求拦截器：校验登录状态
service.interceptors.request.use(
  (config) => {
    // 未登录则终止请求
    if (!isLoggedIn()) {
      ElMessage.warning('请先登录后再操作');
      return Promise.reject(new Error('未登录，请求终止'));
    }
    // 无需添加 JWT Token（Session 认证通过 Cookie 识别）
    return config;
  },
  (error) => {
    ElMessage.error('请求发送失败，请检查网络连接');
    return Promise.reject(error);
  }
);

// 响应拦截器：统一处理错误
service.interceptors.response.use(
  (response) => response.data, // 直接返回响应体（简化前端调用）
  (error) => {
    const status = error.response?.status;
    const errorMsg = error.response?.data?.message || error.message || '请求失败，请重试';

    switch (status) {
      // 401：未登录或 Session 过期
      case 401:
        ElMessage.error('登录状态已失效，请重新登录');
        logout(); // 清除本地登录状态
        window.location.reload(); // 刷新页面，触发登录页显示
        break;
      // 403：无权限
      case 403:
        ElMessage.error('您没有权限执行该操作');
        break;
      // 404：接口不存在
      case 404:
        ElMessage.error('接口地址错误，请联系管理员');
        break;
      // 500：服务器错误
      case 500:
        ElMessage.error(`服务器错误：${errorMsg}`);
        break;
      // 其他错误
      default:
        ElMessage.error(errorMsg);
    }
    return Promise.reject(error);
  }
);

export default service;