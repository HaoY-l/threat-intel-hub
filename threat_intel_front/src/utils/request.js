// src/utils/request.js (修改后的内容)
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { isLoggedIn, logout, getCurrentUser } from './auth';

// 核心修改：无论开发环境还是生产环境，baseURL 都设置为 '/api'
const BASE_URL = '/'; 

// 创建 Axios 实例（适配 Session 认证）
const service = axios.create({
  baseURL: BASE_URL,
  timeout: 8000, 
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true, 
});

// ✅ 白名单列表：不需要登录校验的接口路径
const whiteList = ['/api/auth/login']; 

// 请求拦截器：校验登录状态
service.interceptors.request.use(
  (config) => {
    // 检查请求路径是否在白名单中
    // config.url 是相对路径，例如 '/auth/login'
    const isLoginRequest = whiteList.some(path => config.url === path);

    // 未登录且不是登录请求，则终止请求
    if (!isLoggedIn() && !isLoginRequest) {
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
        // 🚨 404 错误通常是路径问题
        break;
      case 500:
        ElMessage.error(`服务器错误：${errorMsg}`);
        break;
      default:
        ElMessage.error(errorMsg);
    }
    return Promise.reject(error);
  }
);

export default service;