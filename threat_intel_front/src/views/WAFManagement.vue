<template>
  <div class="waf-management">
    <h2>WAF 黑白名单管理</h2>

    <!-- 白名单列表区域 -->
    <section class="white-list">
      <h3>白名单列表</h3>
      <div class="actions">
        <button @click="fetchWhiteList" :disabled="loading">刷新白名单</button>
      </div>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>规则ID</th>
              <th>规则名称</th>
              <th>模板ID</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in pagedWhiteList" :key="item.rule_id">
              <td>{{ item.rule_id }}</td>
              <td>{{ item.rule_name }}</td>
              <td>{{ item.rule_template }}</td>
              <td>
                <button @click="deleteWhite(item.rule_id)" :disabled="loading">删除</button>
              </td>
            </tr>
            <tr v-if="whiteList.length === 0">
              <td colspan="4" class="empty-row">暂无白名单数据</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pagination" v-if="whiteList.length > whitePageSize">
        <button :disabled="whitePage === 1" @click="whitePage--">上一页</button>
        <span>第 {{ whitePage }} 页 / 共 {{ whitePageCount }} 页</span>
        <button :disabled="whitePage === whitePageCount" @click="whitePage++">下一页</button>
      </div>

      <h4>添加白名单</h4>
      <form @submit.prevent="addWhite" class="add-form">
        <label>
          规则名称：
          <input v-model="newWhiteName" required placeholder="输入规则名称" />
        </label>
        <label>
          IP 地址：
          <input v-model="newWhiteIP" required placeholder="输入IP地址" />
        </label>
        <button type="submit" :disabled="loading">添加白名单</button>
      </form>
    </section>

    <!-- 黑名单列表区域 -->
    <section class="black-list">
      <h3>黑名单IP列表</h3>
      <div class="actions">
        <button @click="fetchBlackList" :disabled="loading">刷新黑名单</button>
      </div>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>IP地址</th>
              <th>规则ID</th>
              <th>模板ID</th>
              <th>模板名称</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in pagedBlackList" :key="item.ip + '-' + index">
              <td>{{ item.ip }}</td>
              <td>{{ item.rule_id }}</td>
              <td>{{ item.template_id }}</td>
              <td>{{ item.rule_name }}</td>
            </tr>
            <tr v-if="blackList.length === 0">
              <td colspan="4" class="empty-row">暂无黑名单数据</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pagination" v-if="blackList.length > blackPageSize">
        <button :disabled="blackPage === 1" @click="blackPage--">上一页</button>
        <span>第 {{ blackPage }} 页 / 共 {{ blackPageCount }} 页</span>
        <button :disabled="blackPage === blackPageCount" @click="blackPage++">下一页</button>
      </div>

      <h4>添加黑名单IP</h4>
      <form @submit.prevent="addBlack" class="add-form">
        <label>
          IP 地址：
          <input v-model="newBlackIP" required placeholder="输入IP地址" />
        </label>
        <button type="submit" :disabled="loading">添加黑名单IP</button>
      </form>
    </section>

    <!-- 提示信息 -->
    <div v-if="errorMsg" class="error">{{ errorMsg }}</div>
    <div v-if="successMsg" class="success">{{ successMsg }}</div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'WAFManagement',
  data() {
    return {
      whiteList: [],
      blackList: [], // 结构：[{ ip, rule_id, template_id, rule_name }]
      newWhiteName: '',
      newWhiteIP: '',
      newBlackIP: '',
      loading: false,
      errorMsg: '',
      successMsg: '',

      // 分页状态
      whitePage: 1,
      whitePageSize: 8,
      blackPage: 1,
      blackPageSize: 8
    }
  },
  computed: {
    whitePageCount() {
      return Math.ceil(this.whiteList.length / this.whitePageSize) || 1
    },
    blackPageCount() {
      return Math.ceil(this.blackList.length / this.blackPageSize) || 1
    },
    pagedWhiteList() {
      const start = (this.whitePage - 1) * this.whitePageSize
      return this.whiteList.slice(start, start + this.whitePageSize)
    },
    pagedBlackList() {
      const start = (this.blackPage - 1) * this.blackPageSize
      return this.blackList.slice(start, start + this.blackPageSize)
    }
  },
  watch: {
    whitePage(newVal) {
      if (newVal < 1) this.whitePage = 1
      if (newVal > this.whitePageCount) this.whitePage = this.whitePageCount
    },
    blackPage(newVal) {
      if (newVal < 1) this.blackPage = 1
      if (newVal > this.blackPageCount) this.blackPage = this.blackPageCount
    }
  },
  mounted() {
    this.fetchWhiteList()
    this.fetchBlackList()
  },
  methods: {
    async fetchWhiteList() {
      this.errorMsg = ''
      this.successMsg = ''
      this.loading = true
      try {
        const res = await axios.get('/api/listwhite')
        if (res.data && res.data.message) {
          this.whiteList = res.data.message
          this.whitePage = 1
        } else {
          this.whiteList = []
          this.errorMsg = '白名单数据格式异常'
        }
      } catch (err) {
        this.errorMsg = '获取白名单失败: ' + (err.response?.data?.message || err.message)
      } finally {
        this.loading = false
      }
    },
    async fetchBlackList() {
      this.errorMsg = ''
      this.successMsg = ''
      this.loading = true
      try {
        const res = await axios.get('/api/descblackrule')
        if (res.data && res.data.message && res.data.message.length > 0) {
          // 后端只返回了一个对象，里面有 ip_list，rule_id, rule_name, template_id
          // 展开成多个对象，方便展示
          const msg = res.data.message[0]
          const ipList = msg.ip_list || []
          this.blackList = ipList.map(ip => ({
            ip,
            rule_id: msg.rule_id,
            template_id: msg.template_id,
            rule_name: msg.rule_name
          }))
          this.blackPage = 1
        } else {
          this.blackList = []
          this.errorMsg = '黑名单数据格式异常或无数据'
        }
      } catch (err) {
        this.errorMsg = '获取黑名单失败: ' + (err.response?.data?.message || err.message)
      } finally {
        this.loading = false
      }
    },
    async deleteWhite(ruleId) {
      if (!confirm(`确认删除白名单规则 ID: ${ruleId} 吗？`)) return
      this.errorMsg = ''
      this.successMsg = ''
      this.loading = true
      try {
        const res = await axios.post('/api/deletewhite', { rule_id: ruleId })
        if (res.data && (res.data.code === 200 || res.data.msg === '删除成功')) {
          this.successMsg = '删除成功'
          await this.fetchWhiteList()
        } else {
          this.errorMsg = '删除失败'
        }
      } catch (err) {
        this.errorMsg = '删除失败: ' + (err.response?.data?.message || err.message)
      } finally {
        this.loading = false
      }
    },
    async addWhite() {
      if (!this.newWhiteName.trim() || !this.newWhiteIP.trim()) {
        this.errorMsg = '请输入完整白名单信息'
        return
      }
      this.errorMsg = ''
      this.successMsg = ''
      this.loading = true

      const payload = [
        {
          name: this.newWhiteName.trim(),
          tags: ['waf'],
          status: 1,
          origin: 'custom',
          conditions: [
            {
              key: 'IP',
              opValue: 'contain',
              subKey: '',
              values: this.newWhiteIP.trim()
            }
          ]
        }
      ]
      try {
        const res = await axios.post('/api/addwhite', payload)
        if (res.data && res.data.status === 'success') {
          this.successMsg = '白名单添加成功'
          this.newWhiteName = ''
          this.newWhiteIP = ''
          await this.fetchWhiteList()
        } else {
          this.errorMsg = '添加失败'
        }
      } catch (err) {
        this.errorMsg = '添加失败: ' + (err.response?.data?.message || err.message)
      } finally {
        this.loading = false
      }
    },
    async addBlack() {
      if (!this.newBlackIP.trim()) {
        this.errorMsg = '请输入黑名单IP'
        return
      }
      this.errorMsg = ''
      this.successMsg = ''
      this.loading = true
      try {
        const res = await axios.post('/api/modifyblackrule', {
          black_ip: this.newBlackIP.trim()
        })
        this.successMsg = '黑名单添加成功'
        this.newBlackIP = ''
        this.fetchBlackList()
      } catch (err) {
        this.errorMsg = '添加黑名单失败: ' + (err.response?.data?.message || err.message)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.waf-management {
  padding: 2rem;
  color: #fff;
  background: linear-gradient(135deg, #0f0f23 0%, #1a0033 50%, #0f0f23 100%);
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

h2, h3, h4 {
  margin-bottom: 1rem;
}

.actions {
  margin-bottom: 0.5rem;
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid #444;
  border-radius: 6px;
  margin-bottom: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

thead {
  background-color: #222244;
}

thead th {
  padding: 0.7rem 1rem;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #4a4aff;
}

tbody tr:nth-child(odd) {
  background-color: #111133;
}

tbody tr:hover {
  background-color: #2a2a7a;
}

td {
  padding: 0.6rem 1rem;
  border-bottom: 1px solid #333366;
}

.empty-row {
  text-align: center;
  color: #8888aa;
}

button {
  cursor: pointer;
  background-color: #4a4aff;
  color: white;
  border: none;
  padding: 0.4rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s ease;
  font-weight: 600;
  user-select: none;
}

button:disabled {
  background-color: #888;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #2727ff;
}

form.add-form {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
  margin-top: 1rem;
}

form.add-form label {
  display: flex;
  flex-direction: column;
  font-weight: 500;
  color: #ccc;
  min-width: 200px;
}

form.add-form input {
  width: 100%;
  padding: 0.4rem 0.6rem;
  border-radius: 4px;
  border: 1px solid #666;
  background: #222;
  color: #fff;
  font-size: 1rem;
  margin-top: 0.3rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  user-select: none;
}

.pagination button {
  min-width: 80px;
}

.error {
  margin-top: 1rem;
  color: #ff4c4c;
  font-weight: 600;
  text-align: center;
}

.success {
  margin-top: 1rem;
  color: #4cff4c;
  font-weight: 600;
  text-align: center;
}
</style>
