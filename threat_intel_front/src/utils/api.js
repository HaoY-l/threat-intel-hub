// src/utils/api.js (修改后的内容)
import axios from 'axios'

// 核心修改：无论开发环境还是生产环境，baseURL 都设置为 '/api'
const BASE_URL = '/api';

// 创建axios实例
const api = axios.create({
  baseURL: BASE_URL, 
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true, 
})

// ... (拦截器保持不变)

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// ✅ 获取所有 CVE 数据
export const getAllCVE = async () => {
  try {
    const res = await api.get('/cve')  
    return res 
  } catch (error) {
    throw error
  }
}

// ✅ 查询威胁情报接口
export const queryThreatIntel = async (queryObj) => {
  try {
    const res = await api.post('/query', queryObj) 
    return res
  } catch (error) {
    throw error
  }
}

/**
 * 获取新闻数据
 */
export async function getNewsData() {
  try {
    // 请求路径现在是 /api/news
    const responseData = await api.get('/news');
    console.log('getNewsData responseData:', responseData);
    return responseData; 
  } catch (error) {
    console.error('Error fetching news data:', error);
    throw error;
  }
}