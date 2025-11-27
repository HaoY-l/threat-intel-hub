// src/utils/request.js (修改后的内容)
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { isLoggedIn, logout, getCurrentUser } from './auth';

// 核心修改：无论开发环境还是生产环境，baseURL 都设置为 '/api'
// 这样请求会变成 /api/cve, /api/news 等。
// - 本地开发: 通过 vite.config.js 代理到 http://localhost:8891/api
// - 容器部署: 请求直接发送到 http://10.130.201.29:8891/api (这是后端期望的路径)
const BASE_URL = '/api'; 

// 创建 Axios 实例（适配 Session 认证）
const service = axios.create({
  baseURL: BASE_URL,
  timeout: 8000, 
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true, 
});

// ... (请求拦截器和响应拦截器保持不变)

// 请求拦截器：校验登录状态
service.interceptors.request.use(
  (config) => {
    // 未登录则终止请求
    if (!isLoggedIn()) {
      ElMessage.warning('请先登录后再操作');
      return Promise.reject(new Error('未登录，请求终止'));
    }
    return config;
  },
  (error) => {
    ElMessage.error('请求发送失败，请检查网络连接');
    return Promise.reject(error);
  }
);

// 响应拦截器：统一处理错误
service.interceptors.response.use(
  (response) => response.data, // 直接返回响应体
  (error) => {
    const status = error.response?.status;
    const errorMsg = error.response?.data?.message || error.message || '请求失败，请重试';

    switch (status) {
      case 401:
        ElMessage.error('登录状态已失效，请重新登录');
        logout(); 
        window.location.reload(); 
        break;
      case 403:
        ElMessage.error('您没有权限执行该操作');
        break;
      case 404:
        ElMessage.error('接口地址错误，请联系管理员');
        // 🚨 404 错误通常是路径问题，现在我们修复了 /api 前缀，应该能解决大部分 404
        break;
      case 500:
        ElMessage.error(`服务器错误：${errorMsg}`);
        // 🚨 **/api/descblackrule** 接口报 500，需要检查后端代码
        break;
      default:
        ElMessage.error(errorMsg);
    }
    return Promise.reject(error);
  }
);

export default service;