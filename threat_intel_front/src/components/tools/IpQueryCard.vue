<template>
  <div class="tool-card">
    <h2>IP归属地查询</h2>

    <div class="controls">
      <label>
        IP地址：
        <input type="text" v-model="ipAddress" placeholder="例如: 8.8.8.8" />
      </label>

      <button @click="queryIp" :disabled="isLoading">
        {{ isLoading ? '查询中...' : '查询' }}
      </button>
    </div>

    <div class="status">
      <p>查询结果：</p>
      <pre v-if="ipInfo && ipInfo.success" class="success-response">
        IP:       {{ ipInfo.ip }}
        国家:     {{ ipInfo.country }}
        城市:     {{ ipInfo.city }}
        运营商:   {{ ipInfo.isp }}
      </pre>
      <pre v-else-if="error" class="error-response">
        ❌ 请求失败: {{ error }}
      </pre>
      <p v-else-if="!ipAddress">请输入IP地址</p>
      <p v-else-if="isLoading">正在查询...</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IpQueryCard',
  data() {
    return {
      ipAddress: '',
      ipInfo: null,
      isLoading: false,
      error: ''
    }
  },
  methods: {
    async queryIp() {
      if (!this.ipAddress) {
        this.error = 'IP地址不能为空'
        this.ipInfo = null
        return
      }

      this.isLoading = true
      this.error = ''
      this.ipInfo = null

      try {
        const res = await fetch(`/api/ip_query?ip=${this.ipAddress}`)
        const data = await res.json()

        if (data.success) {
          this.ipInfo = data
        } else {
          this.error = data.message || '查询失败'
        }
      } catch (err) {
        this.error = '❌ 请求失败: ' + err.message
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
/* 样式与之前相同，无需更改 */
.tool-card {
  padding: 2rem;
  color: #fff;
  background-color: #2c2c3c;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  flex: 1 1 45%;
  min-width: 300px;
}

h2 {
  margin-top: 0;
  border-bottom: 2px solid #4caf50;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}

.controls {
  margin: 1rem 0;
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.controls input {
  width: 150px;
  padding: 0.5rem;
  border-radius: 5px;
  border: 1px solid #444;
  background-color: #333;
  color: #fff;
}

.controls button {
  background-color: #4caf50;
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.controls button:disabled {
  background-color: #aaa;
  cursor: not-allowed;
}

.controls button:hover:not(:disabled) {
  background-color: #45a049;
}

.status {
  margin-top: 1rem;
  font-size: 0.9rem;
}

.status pre {
  background: #333;
  padding: 1rem;
  border-radius: 5px;
  white-space: pre-wrap;
  color: #0f0;
}
.error-response {
  color: #ff5555;
}
</style>