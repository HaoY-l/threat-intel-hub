<template>
  <div class="tool-card">
    <h2>域名 Whois 查询</h2>

    <div class="controls">
      <label>
        域名：
        <input type="text" v-model="domainName" placeholder="例如: google.com" />
      </label>

      <button @click="queryWhois" :disabled="isLoading">
        {{ isLoading ? '查询中...' : '查询' }}
      </button>
    </div>

    <div class="status">
      <p>查询结果：</p>
      <pre v-if="whoisInfo && whoisInfo.success" class="success-response">
        域名:             {{ whoisInfo.domain_name }}
        注册商:           {{ whoisInfo.registrar }}
        注册日期:         {{ whoisInfo.creation_date }}
        过期日期:         {{ whoisInfo.expiration_date }}
        最后更新时间:     {{ whoisInfo.updated_date }}
        域名状态:         {{ whoisInfo.status }}
        域名服务器:       {{ Array.isArray(whoisInfo.name_servers) ? whoisInfo.name_servers.join(', ') : whoisInfo.name_servers }}
      </pre>
      <pre v-else-if="error" class="error-response">
        ❌ 请求失败: {{ error }}
      </pre>
      <p v-else-if="!domainName">请输入域名</p>
      <p v-else-if="isLoading">正在查询...</p>
      <p v-else-if="whoisInfo && !whoisInfo.success">未找到 Whois 信息或域名无效。</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DomainWhoisCard',
  data() {
    return {
      domainName: '',
      whoisInfo: null,
      isLoading: false,
      error: ''
    }
  },
  methods: {
    async queryWhois() {
      if (!this.domainName) {
        this.error = '域名不能为空'
        this.whoisInfo = null
        return
      }

      this.isLoading = true
      this.error = ''
      this.whoisInfo = null

      try {
        const res = await fetch(`/api/whois_query?domain=${this.domainName}`)
        const data = await res.json()

        if (data.success) {
          this.whoisInfo = data
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
/* 保持与 IpQueryCard.vue 相同的样式，以保持一致性 */
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