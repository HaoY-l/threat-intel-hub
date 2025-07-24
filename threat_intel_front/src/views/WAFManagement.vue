<template>
  <div class="waf-management">
    <div class="header">
      <div class="header-left">
        <h1>WAF 安全管理中心</h1>
        <p class="header-subtitle">实时监控与威胁防护</p>
      </div>
      <div class="header-actions">
        <button @click="refreshAllData" :disabled="loading" class="refresh-btn">
          <i class="fa fa-refresh mr-2"></i>
          <span>刷新数据</span>
        </button>
      </div>
    </div>

    <WAFOverview :statsOverview="statsOverview" />

    <div class="monitoring-grid">
      <WAFMonitoringPanel
        :blockedIPs="blockedIPs"
        :blockedTimeRange="blockedTimeRange"
        :highFreqIPs="highFreqIPs"
        :freqTimeRange="freqTimeRange"
        @update:blockedTimeRange="blockedTimeRange = $event"
        @update:freqTimeRange="freqTimeRange = $event"
        @fetchBlockedIPs="fetchBlockedIPs"
        @fetchHighFreqIPs="fetchHighFreqIPs"
        @addToBlacklist="addToBlacklist"
        @blockIP="blockIP"
      />

      <WAFAutoProtection
        :autoProtectionEnabled="autoProtectionEnabled"
        :threatIntelligenceEnabled="threatIntelligenceEnabled"
        :autoBlockEnabled="autoBlockEnabled"
        :aiLearningEnabled="aiLearningEnabled"
        :autoBlockedCount="autoBlockedCount"
        :todayThreats="todayThreats"
      />
    </div>

    <WAFManagementPanel
      :whiteList="whiteList"
      :blackList="blackList"
      :whitePage="whitePage" @update:whitePage="whitePage = $event"
      :blackPage="blackPage" @update:blackPage="blackPage = $event"
      :newWhiteName="newWhiteName"
      :newWhiteIP="newWhiteIP"
      :newWhiteRemark="newWhiteRemark"
      :newBlackIP="newBlackIP"
      :newBlackReason="newBlackReason"
      :newBlackDuration="newBlackDuration"
      :loading="loading"
      @update:newWhiteName="newWhiteName = $event"
      @update:newWhiteIP="newWhiteIP = $event"
      @update:newWhiteRemark="newWhiteRemark = $event"
      @update:newBlackIP="newBlackIP = $event"
      @update:newBlackReason="newBlackReason = $event"
      @update:newBlackDuration="newBlackDuration = $event"
      @fetchWhiteList="fetchWhiteList"
      @fetchBlackList="fetchBlackList"
      @deleteWhite="deleteWhite"
      @deleteBlack="deleteBlack"
      @addWhite="addWhite"
      @addBlack="addBlack"
      @showError="showError"
      @showSuccess="showSuccess"
    />

    <transition name="message">
      <div v-if="errorMsg" class="message error">
        <i class="message-icon fa fa-exclamation-circle"></i>
        <span>{{ errorMsg }}</span>
        <button @click="errorMsg = ''" class="close-btn">×</button>
      </div>
    </transition>

    <transition name="message">
      <div v-if="successMsg" class="message success">
        <i class="message-icon fa fa-check-circle"></i>
        <span>{{ successMsg }}</span>
        <button @click="successMsg = ''" class="close-btn">×</button>
      </div>
    </transition>

    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>正在加载数据...</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import WAFOverview from '../components/waf/WAFOverview.vue';
import WAFMonitoringPanel from '../components/waf/WAFMonitoringPanel.vue';
import WAFAutoProtection from '../components/waf/WAFAutoProtection.vue';
import WAFManagementPanel from '../components/waf/WAFManagementPanel.vue';

export default {
  name: 'WAFManagement',
  components: {
    WAFOverview,
    WAFMonitoringPanel,
    WAFAutoProtection,
    WAFManagementPanel
  },
  data() {
    return {
      // 数据
      whiteList: [],
      blackList: [],
      blockedIPs: [],
      highFreqIPs: [],

      // 表单
      newWhiteName: '',
      newWhiteIP: '',
      newWhiteRemark: '',
      newBlackIP: '',
      newBlackReason: '恶意扫描',
      newBlackDuration: '24h',

      // 状态
      loading: false,
      errorMsg: '',
      successMsg: '',

      // 时间范围，默认设置为 'today'
      blockedTimeRange: 'today', // 默认查询今天的数据
      freqTimeRange: 'today', // 默认查询今天的数据

      // 分页
      whitePage: 1, // 父组件维护白名单当前页码
      whitePageSize: 5,
      blackPage: 1, // 父组件维护黑名单当前页码
      blackPageSize: 5,

      // 统计数据
      autoBlockedCount: 0,
      todayThreats: 0,

      // 防护状态
      autoProtectionEnabled: true,
      threatIntelligenceEnabled: true,
      autoBlockEnabled: true,
      aiLearningEnabled: true,
    }
  },

  computed: {
    statsOverview() {
      return [
        {
          key: 'whitelist',
          title: '白名单规则',
          value: this.whiteList.length,
          icon: 'fa-shield',
          iconClass: 'bg-green-500',
          color: 'linear-gradient(135deg, #4CAF50, #45a049)',
          trendClass: 'text-green-500',
          trendIcon: 'fa-arrow-up'
        },
        {
          key: 'blacklist',
          title: '黑名单IP',
          value: this.blackList.length,
          icon: 'fa-ban',
          iconClass: 'bg-red-500',
          color: 'linear-gradient(135deg, #f44336, #d32f2f)',
          trendClass: 'text-red-500',
          trendIcon: 'fa-arrow-up'
        },
        {
          key: 'blocked',
          title: '规则封禁',
          value: this.blockedIPs.length,
          icon: 'fa-exclamation-triangle',
          iconClass: 'bg-orange-500',
          color: 'linear-gradient(135deg, #FF9800, #F57C00)',
          trendClass: 'text-green-500',
          trendIcon: 'fa-arrow-down'
        },
        {
          key: 'highfreq',
          title: '高频监控',
          value: this.highFreqIPs.length,
          icon: 'fa-line-chart',
          iconClass: 'bg-blue-500',
          color: 'linear-gradient(135deg, #2196F3, #1976D2)',
          trendClass: 'text-red-500',
          trendIcon: 'fa-arrow-up'
        },
        {
          key: 'threatblock',
          title: '威胁情报自动封禁',
          value: this.todayThreats,
          icon: 'fa-bolt',
          iconClass: 'bg-purple-500',
          color: 'linear-gradient(135deg, #8A2BE2, #9932CC)',
          trendClass: 'text-purple-500',
          trendIcon: 'fa-arrow-up'
        }
      ]
    },
  },

  mounted() {
    this.initData();
    this.setupAutoRefresh();
  },

  beforeUnmount() {
    clearInterval(this.refreshInterval);
  },

  methods: {
    async initData() {
      // 首次加载时，fetchBlockedIPs 和 fetchHighFreqIPs 会根据默认的 'today' 进行查询
      await this.refreshAllData();
    },

    setupAutoRefresh() {
      // 每30秒自动刷新监控数据
      this.refreshInterval = setInterval(() => {
        // 自动刷新时，保持当前选择的时间范围
        this.fetchBlockedIPs();
        this.fetchHighFreqIPs();
      }, 30000);
    },

    async refreshAllData() {
      this.loading = true;
      try {
        await Promise.all([
          this.fetchWhiteList(),
          this.fetchBlackList(),
          this.fetchBlockedIPs(), // 调用时会根据 blockedTimeRange 计算时间
          this.fetchHighFreqIPs(), // 调用时会根据 freqTimeRange 计算时间
          this.fetchProtectionStats()
        ]);
        this.showSuccess('数据刷新成功');
      } catch (error) {
        this.showError('数据刷新失败');
        console.error('刷新数据失败:', error);
      } finally {
        this.loading = false;
      }
    },

    showError(msg) {
      this.errorMsg = msg;
      setTimeout(() => { this.errorMsg = ''; }, 3000); // 3秒后自动消失
    },

    showSuccess(msg) {
      this.successMsg = msg;
      setTimeout(() => { this.successMsg = ''; }, 3000); // 3秒后自动消失
    },

    /**
     * 根据选择的时间范围类型（'today', '3d', '7d', '1m'）计算 from 和 to 时间。
     * @param {string} rangeType 'today', '3d', '7d', '1m'
     * @returns {{from: string, to: string}} 格式化后的时间字符串对象
     */
    getDateTimeRange(rangeType) {
      const now = new Date();
      let fromDate;
      let toDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), now.getMinutes(), now.getSeconds()); // 精确到秒的当前时间

      switch (rangeType) {
        case 'today':
          fromDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0); // 当天零点
          break;
        case '3d':
          fromDate = new Date(now);
          fromDate.setDate(now.getDate() - 3); // 3天前
          fromDate.setHours(0, 0, 0, 0); // 从3天前零点开始
          break;
        case '7d':
          fromDate = new Date(now);
          fromDate.setDate(now.getDate() - 7); // 7天前
          fromDate.setHours(0, 0, 0, 0); // 从7天前零点开始
          break;
        case '1m': // 1个月，粗略按30天计算
          fromDate = new Date(now);
          fromDate.setMonth(now.getMonth() - 1); // 1个月前
          fromDate.setHours(0, 0, 0, 0); // 从1个月前零点开始
          break;
        default: // 如果有其他分钟数选项，可以这样处理，但目前用户只指定了今天/天/月
          const minutes = parseInt(rangeType);
          if (!isNaN(minutes)) {
             fromDate = new Date(now.getTime() - minutes * 60 * 1000); // 从当前时间回溯指定分钟数
          } else {
             fromDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0); // 默认今天零点
          }
          break;
      }

      const format = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
      };

      return {
        from: format(fromDate),
        to: format(toDate)
      };
    },

    // API 调用方法
    async fetchWhiteList() {
      try {
        const res = await axios.get('/api/listwhite');
        if (res.data && res.data.message) {
          this.whiteList = res.data.message;
        } else {
          this.whiteList = [];
        }
      } catch (err) {
        console.error('获取白名单失败:', err);
        this.showError('获取白名单失败');
      }
    },

    async fetchBlackList() {
      try {
        const res = await axios.get('/api/descblackrule');
        if (res.data && res.data.message && res.data.message.length > 0) {
          const msg = res.data.message[0];
          const ipList = msg.ip_list || [];
          this.blackList = ipList.map(ip => ({
            ip,
            rule_id: msg.rule_id,
            template_id: msg.template_id,
            rule_name: msg.rule_name,
            reason: msg.reason,
            created_at: msg.created_at
          }));
        } else {
          this.blackList = [];
        }
      } catch (err) {
        console.error('获取黑名单失败:', err);
        this.showError('获取黑名单失败');
      }
    },

    async fetchBlockedIPs() {
      try {
        const { from, to } = this.getDateTimeRange(this.blockedTimeRange);
        const res = await axios.get('/api/blocked_ips', {
          params: {
            from: from,
            to: to
          }
        });

        if (res.data && res.data.data) {
          this.blockedIPs = res.data.data.map(item => ({
            ...item,
            threat_level: this.getThreatLevelFromScore(item.threat_score)
          }));
        } else {
          this.blockedIPs = [];
        }
      } catch (err) {
        console.error('获取封禁IP失败:', err);
        this.showError('获取封禁IP失败');
      }
    },

    async fetchHighFreqIPs() {
      try {
        const { from, to } = this.getDateTimeRange(this.freqTimeRange);
        const res = await axios.get('/api/ip_request_frequency', {
          params: {
            from: from,
            to: to
          }
        });

        if (res.data && res.data.data) {
          this.highFreqIPs = res.data.data;
        } else {
          this.highFreqIPs = [];
        }
      } catch (err) {
        console.error('获取高频IP失败:', err);
        this.showError('获取高频IP失败');
      }
    },

    async fetchProtectionStats() {
      try {
        const res = await axios.get('/api/protection_stats');

        if (res.data && res.data.data) {
          const stats = res.data.data;
          this.autoBlockedCount = stats.auto_blocked_count || 0;
          this.todayThreats = stats.today_threats || 0;

          // 更新防护状态
          if (stats.protection_status) {
            this.autoProtectionEnabled = stats.protection_status.auto_protection || true;
            this.threatIntelligenceEnabled = stats.protection_status.threat_intelligence || true;
            this.autoBlockEnabled = stats.protection_status.auto_block || true;
            this.aiLearningEnabled = stats.protection_status.ai_learning || true;
          }
        }
      } catch (err) {
        console.error('获取防护统计数据失败:', err);
      }
    },

    async deleteWhite(ruleId) {
      if (!confirm(`确认删除白名单规则 ID: ${ruleId} 吗？`)) return;

      this.loading = true;
      try {
        const res = await axios.post('/api/deletewhite', { rule_id: ruleId });
        if (res.data && (res.data.code === 200 || res.data.msg === '删除成功')) {
          this.showSuccess('删除成功');
          await this.fetchWhiteList();
        } else {
          this.showError('删除失败');
        }
      } catch (err) {
        this.showError('删除失败: ' + (err.response?.data?.message || err.message));
      } finally {
        this.loading = false;
      }
    },

    async deleteBlack(ip) {
      if (!confirm(`确认从黑名单中移除 ${ip} 吗？`)) return;

      this.loading = true;
      try {
        const res = await axios.post('/api/deleteblack', { ip });
        if (res.data && res.data.status === 'success') {
          this.showSuccess(`IP ${ip} 已从黑名单移除`);
          await this.fetchBlackList();
        } else {
          this.showError('移除失败');
        }
      } catch (err) {
        this.showError('移除失败: ' + (err.response?.data?.message || err.message));
      } finally {
        this.loading = false;
      }
    },

    async addWhite() {
      if (!this.newWhiteName.trim() || !this.newWhiteIP.trim()) {
        this.showError('请输入完整白名单信息');
        return;
      }

      // 简单的IP格式验证
      const ipPattern = /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\/([0-9]|[1-2][0-9]|3[0-2]))?$/;
      if (!ipPattern.test(this.newWhiteIP.trim())) {
        this.showError('请输入有效的IP地址或CIDR范围');
        return;
      }

      this.loading = true;
      const payload = [{
        name: this.newWhiteName.trim(),
        tags: ['waf'],
        status: 1,
        origin: 'custom',
        remark: this.newWhiteRemark,
        conditions: [{
          key: 'IP',
          opValue: 'contain',
          subKey: '',
          values: this.newWhiteIP.trim()
        }]
      }];

      try {
        const res = await axios.post('/api/addwhite', payload);
        if (res.data && res.data.status === 'success') {
          this.showSuccess('白名单添加成功');
          this.newWhiteName = '';
          this.newWhiteIP = '';
          this.newWhiteRemark = '';
          await this.fetchWhiteList();
        } else {
          this.showError('添加失败');
        }
      } catch (err) {
        this.showError('添加失败: ' + (err.response?.data?.message || err.message));
      } finally {
        this.loading = false;
      }
    },

    async addBlack() {
      if (!this.newBlackIP.trim()) {
        this.showError('请输入黑名单IP');
        return;
      }

      // 简单的IP格式验证
      const ipPattern = /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
      if (!ipPattern.test(this.newBlackIP.trim())) {
        this.showError('请输入有效的IP地址');
        return;
      }

      this.loading = true;
      try {
        const res = await axios.post('/api/modifyblackrule', {
          black_ip: this.newBlackIP.trim(),
          reason: this.newBlackReason,
          duration: this.newBlackDuration
        });

        if (res.data && res.data.status === 'success') {
          this.showSuccess('黑名单添加成功');
          this.newBlackIP = '';
          await this.fetchBlackList();
        } else {
          this.showError('添加失败');
        }
      } catch (err) {
        this.showError('添加黑名单失败: ' + (err.response?.data?.message || err.message));
      } finally {
        this.loading = false;
      }
    },

    async addToBlacklist(ip) {
      if (!confirm(`确认将 ${ip} 加入黑名单吗？`)) return;

      this.loading = true;
      try {
        const res = await axios.post('/api/modifyblackrule', {
          black_ip: ip,
          reason: '规则封禁自动添加',
          duration: '7d'
        });

        if (res.data && res.data.status === 'success') {
          this.showSuccess(`IP ${ip} 已成功加入黑名单`);
          await this.fetchBlackList();
        } else {
          this.showError('加入黑名单失败');
        }
      } catch (err) {
        this.showError('加入黑名单失败: ' + (err.response?.data?.message || err.message));
      } finally {
        this.loading = false;
      }
    },

    async blockIP(ip) {
      if (!confirm(`确认封禁IP ${ip} 吗？这将阻止该IP访问您的网站。`)) return;

      this.loading = true;
      try {
        const res = await axios.post('/api/block_ip', {
          ip,
          reason: '高频请求',
          duration: '24h'
        });

        if (res.data && res.data.status === 'success') {
          this.showSuccess(`IP ${ip} 已成功封禁`);
          await Promise.all([
            this.fetchBlockedIPs(),
            this.fetchHighFreqIPs()
          ]);
        } else {
          this.showError('封禁失败');
        }
      } catch (err) {
        this.showError('封禁失败: ' + (err.response?.data?.message || err.message));
      } finally {
        this.loading = false;
      }
    },

    // 工具方法
    getThreatLevelFromScore(score) {
      if (score === undefined || score === null) return 'unknown'; // 应对可能没有 threat_score 的情况
      if (score >= 80) return 'high';
      if (score >= 50) return 'medium';
      return 'low';
    },
  }
}
</script>

<style scoped>
/* 保持不变 */
/* 基础样式 */
.waf-management {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
  color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  padding: 1rem;
}

/* 头部样式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  margin-bottom: 1.5rem;
}

.header-left h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-subtitle {
  margin: 0.5rem 0 0 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.refresh-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box_shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 监控网格 */
.monitoring-grid {
  padding: 0 0 1.5rem 0;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.25rem;
  height: auto;
  min-height: 400px;
}

/* 全局消息 */
.message {
  position: fixed;
  top: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 50;
  box_shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  opacity: 0;
  transform: translateY(-20px);
  transition: all 0.5s ease;
}

.message.error {
  background: rgba(229, 62, 62, 0.95);
  color: white;
}

.message.success {
  background: rgba(56, 161, 105, 0.95);
  color: white;
}

.message-enter-active,
.message-leave-active {
  transition: opacity 0.5s, transform 0.5s;
}

.message-enter-from,
.message-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.message-icon {
  font-size: 1.2rem;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1.2rem;
  margin-left: 1rem;
  opacity: 0.7;
  transition: opacity 0.3s ease;
}

.close-btn:hover {
  opacity: 1;
}

/* 加载中遮罩 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.loading-spinner {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  border-top-color: #667eea;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .monitoring-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 800px) {
  .header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .monitoring-grid {
    grid-template-columns: 1fr;
  }
}
</style>
