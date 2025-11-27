// src/utils/api.js (你第二个提供的文件内容)
import axios from 'axios'

// 核心修改：根据环境设置 baseURL
// 开发环境 (npm run dev): '/api' (触发 vite.config.js 的代理)
// 生产/容器环境 (npm run build): '' (使用相对路径)
const BASE_URL = import.meta.env.DEV ? '/api' : '';

// 创建axios实例
const api = axios.create({
  baseURL: BASE_URL, 
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true, // 确保这个实例也能携带Cookie
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加认证token
    // config.headers.Authorization = `Bearer ${token}`
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data  // 这里已经返回了data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// ✅ 获取所有 CVE 数据（后端应该返回全部或分页）
export const getAllCVE = async () => {
  try {
    const res = await api.get('/cve')  // 对应 Flask 的 GET /api/cve
    return res  // 拦截器已返回data
  } catch (error) {
    throw error
  }
}

// ✅ 查询威胁情报接口
// 后端接口定义为 POST /api/query，注意是 POST，不是 GET！
export const queryThreatIntel = async (queryObj) => {
  try {
    const res = await api.post('/query', queryObj)  // 如 { target: '8.8.8.8', type: 'ip' }
    return res
  } catch (error) {
    throw error
  }
}

/**
 * 获取新闻数据
 * @returns {Promise<Array>} 返回新闻数据数组的 Promise
 */
export async function getNewsData() {
  try {
    // 拦截器已经返回 response.data，所以这里直接获取返回值即可
    const responseData = await api.get('/news');
    console.log('getNewsData responseData:', responseData);
    return responseData; // 返回的是数据本身
  } catch (error) {
    console.error('Error fetching news data:', error);
    throw error;
  }
}