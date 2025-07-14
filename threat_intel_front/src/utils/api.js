import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_APP_API_BASE_URL || 'http://localhost:5001/api',
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
    return response.data
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
    return res
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