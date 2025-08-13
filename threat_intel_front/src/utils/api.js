import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
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
    return res  // 这里正确，因为拦截器已经返回了data
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
    const response = await api.get('/news');
    // 修复：由于响应拦截器已经返回了response.data，这里直接返回response即可
    // 不要再访问response.data，因为response本身就是数据
    console.log('getNewsData response:', response);
    return response;  // 修复：直接返回response，而不是response.data
  } catch (error) {
    console.error('Error fetching news data:', error);
    throw error;
  }
}