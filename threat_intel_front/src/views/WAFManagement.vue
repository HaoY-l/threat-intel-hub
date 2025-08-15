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
        :threatTimeRange="threatTimeRange"
        @update:threatTimeRange="threatTimeRange = $event"
        @fetchProtectionStats="fetchProtectionStats"
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
      blockedIPs: [], // 原始数据，可能包含重复IP（用于监控面板，按时间范围过滤）
      highFreqIPs: [], // 原始数据，可能包含重复IP（用于监控面板，按时间范围过滤）

      // 新增：用于总数统计的去重IP列表
      totalUniqueBlockedIPs: [], // 存储所有时间规则封禁的去重IP
      totalUniqueHighFreqIPs: [], // 存储所有时间高频请求的去重IP
      totalThreatBlockedIPs: [], // 存储所有时间威胁情报自动封禁的去重IP

      // 新增威胁情报时间范围
      threatTimeRange: 'today', // 新增威胁情报时间范围筛选
      // 时间范围，默认设置为 'today'
      blockedTimeRange: 'today',
      freqTimeRange: 'today',

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
      autoBlockedCount: 0, // 可以保持，用于显示当天的事件数
      todayThreats: 0, // 可以保持，用于显示当天的威胁IP数

      // 防护状态
      autoProtectionEnabled: true,
      threatIntelligenceEnabled: true,
      autoBlockEnabled: true,
      aiLearningEnabled: true,
    }
  },

  computed: {
    statsOverview() {
      // 这里的 blockedIPs 和 highFreqIPs 仍然用于监控面板的时间范围统计
      // 对于总数统计，我们使用新的 totalUniqueBlockedIPs, totalUniqueHighFreqIPs 和 totalThreatBlockedIPs

      return [
        {
          key: 'whitelist',
          title: '白名单规则',
          value: this.whiteList.length, // 白名单规则本身通常是唯一的，不需要额外去重
          icon: 'fa-shield',
          iconClass: 'bg-green-500',
          color: 'linear-gradient(135deg, #4CAF50, #45a049)',
          trendClass: 'text-green-500',
          trendIcon: 'fa-arrow-up'
        },
        {
          key: 'blacklist',
          title: '黑名单IP',
          value: this.blackList.length, // 黑名单IP也应该是唯一的
          icon: 'fa-ban',
          iconClass: 'bg-red-500',
          color: 'linear-gradient(135deg, #f44336, #d32f2f)',
          trendClass: 'text-red-500',
          trendIcon: 'fa-arrow-up'
        },
        {
          key: 'blocked',
          title: '规则封禁IP（去重总数）', // 标题改为“去重总数”
          value: this.totalUniqueBlockedIPs.length, // 使用新的总去重IP数据
          icon: 'fa-exclamation-triangle',
          iconClass: 'bg-orange-500',
          color: 'linear-gradient(135deg, #FF9800, #F57C00)',
          trendClass: 'text-green-500',
          trendIcon: 'fa-arrow-down'
        },
        {
          key: 'highfreq',
          title: '高频请求IP（去重总数）', // 标题改为“去重总数”
          value: this.totalUniqueHighFreqIPs.length, // 使用新的总去重IP数据
          icon: 'fa-line-chart',
          iconClass: 'bg-blue-500',
          color: 'linear-gradient(135deg, #2196F3, #1976D2)',
          trendClass: 'text-red-500',
          trendIcon: 'fa-arrow-up'
        },
        {
          key: 'threatblock',
          title: '威胁情报自动封禁（去重总数）', // 标题改为“去重总数”
          value: this.totalThreatBlockedIPs.length, // 使用新的总去重IP数据
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
      await this.refreshAllData();
    },

    setupAutoRefresh() {
      this.refreshInterval = setInterval(() => {
        // 刷新监控面板数据（基于当前选定的时间范围）
        this.fetchBlockedIPs();
        this.fetchHighFreqIPs();
        this.fetchProtectionStats();

        // 刷新总数统计数据（获取所有历史数据）
        this.fetchBlockedIPs('all');
        this.fetchHighFreqIPs('all');
        this.fetchProtectionStats('all');
      }, 30000); // 每30秒刷新一次
    },

    async refreshAllData() {
      this.loading = true;
      try {
        await Promise.all([
          this.fetchWhiteList(),
          this.fetchBlackList(),
          // 获取监控面板数据 (today/当前时间范围)
          this.fetchBlockedIPs(),
          this.fetchHighFreqIPs(),
          this.fetchProtectionStats(),
          // 获取总数统计数据 (all time)
          this.fetchBlockedIPs('all'),
          this.fetchHighFreqIPs('all'),
          this.fetchProtectionStats('all')
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
      setTimeout(() => { this.errorMsg = ''; }, 3000);
    },

    showSuccess(msg) {
      this.successMsg = msg;
      setTimeout(() => { this.successMsg = ''; }, 3000);
    },

    getDateTimeRange(rangeType) {
      const now = new Date();
      let fromDate;
      // toDate 设置为当前精确时间
      let toDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), now.getMinutes(), now.getSeconds());

      if (rangeType === 'all') { // 新增 'all' 类型，表示从 Unix Epoch 开始
          fromDate = new Date(0); // 1970-01-01 00:00:00 UTC
      } else {
        switch (rangeType) {
          case 'today':
            fromDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
            break;
          case '3d':
            fromDate = new Date(now);
            fromDate.setDate(now.getDate() - 3);
            fromDate.setHours(0, 0, 0, 0);
            break;
          case '7d':
            fromDate = new Date(now);
            fromDate.setDate(now.getDate() - 7);
            fromDate.setHours(0, 0, 0, 0);
            break;
          case '1m':
            fromDate = new Date(now);
            fromDate.setMonth(now.getMonth() - 1);
            fromDate.setHours(0, 0, 0, 0);
            break;
          default:
            const minutes = parseInt(rangeType);
            if (!isNaN(minutes)) {
               fromDate = new Date(now.getTime() - minutes * 60 * 1000);
            } else {
               fromDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
            }
            break;
        }
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
          // 注意：如果 blackList 数组中的每个对象代表一个黑名单规则，且一个规则下有多个 IP，
          // 那么这里去重 IP 可能不准确，需要根据后端黑名单规则的实际结构来决定。
          // 假设黑名单列表的 length 统计的是规则数量。
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

    // 增加了 fetchType 参数，默认为 'timeRange'
    async fetchBlockedIPs(fetchType = 'timeRange') {
      try {
        const timeRange = fetchType === 'all' ? 'all' : this.blockedTimeRange;
        const { from, to } = this.getDateTimeRange(timeRange);
        const res = await axios.get('/api/blocked_ips', {
          params: {
            from: from,
            to: to
          }
        });

        if (res.data && res.data.data) {
          const processedData = res.data.data.map(item => ({
            ...item,
            threat_level: this.getThreatLevelFromScore(item.threat_score)
          }));

          if (fetchType === 'all') {
            // 获取所有时间的去重IP，用于总览统计
            this.totalUniqueBlockedIPs = [...new Set(processedData.map(item => item.ip))];
          } else {
            // 否则，用于监控面板，保留原始数据（可能包含重复）
            this.blockedIPs = processedData;
          }
        } else {
          if (fetchType === 'all') {
            this.totalUniqueBlockedIPs = [];
          } else {
            this.blockedIPs = [];
          }
        }
      } catch (err) {
        console.error('获取封禁IP失败:', err);
        if (fetchType === 'timeRange') { // 只在监控面板数据获取失败时显示错误
            this.showError('获取封禁IP失败');
        }
      }
    },

    // 增加了 fetchType 参数，默认为 'timeRange'
    async fetchHighFreqIPs(fetchType = 'timeRange') {
      try {
        const timeRange = fetchType === 'all' ? 'all' : this.freqTimeRange;
        const { from, to } = this.getDateTimeRange(timeRange);
        const res = await axios.get('/api/ip_request_frequency', {
          params: {
            from: from,
            to: to
          }
        });

        if (res.data && res.data.data) {
          if (fetchType === 'all') {
            // 获取所有时间的去重IP，用于总览统计
            this.totalUniqueHighFreqIPs = [...new Set(res.data.data.map(item => item.ip))];
          } else {
            // 否则，用于监控面板
            this.highFreqIPs = res.data.data;
          }
        } else {
          if (fetchType === 'all') {
            this.totalUniqueHighFreqIPs = [];
          } else {
            this.highFreqIPs = [];
          }
        }
      } catch (err) {
        console.error('获取高频IP失败:', err);
        if (fetchType === 'timeRange') { // 只在监控面板数据获取失败时显示错误
            this.showError('获取高频IP失败');
        }
      }
    },

    // 增加了 fetchType 参数，默认为 'timeRange'
    async fetchProtectionStats(fetchType = 'timeRange') {
      try {
        // 根据 fetchType 决定使用哪个时间范围
        let timeRange;
        if (fetchType === 'all') {
          timeRange = 'all';
        } else {
          timeRange = this.threatTimeRange; // 使用威胁情报专用的时间范围
        }
        
        const { from, to } = this.getDateTimeRange(timeRange);
        const response = await axios.get('/api/protected_ip', {
          params: {
            from: from,
            to: to
          }
        });
        const records = response.data;

        if (fetchType === 'all') {
          // 获取所有时间的威胁情报自动封禁去重IP
          const uniqueThreatIPs = new Set();
          records.forEach(record => {
            // 检查多种可能的封禁状态字段
            if (record.action === 'blacklisted' || 
                record.action === 'blocked' || 
                record.status === 'blocked' ||
                record.is_blocked === true ||
                record.blocked === true) {
              uniqueThreatIPs.add(record.ip);
            }
          });
          this.totalThreatBlockedIPs = Array.from(uniqueThreatIPs);
        } else {
          // 统计当前时间范围的自动封禁数量和去重IP数量
          let blockedCount = 0;
          const uniqueThreatIPsInRange = new Set();

          records.forEach(record => {
            // 检查多种可能的封禁状态字段
            if (record.action === 'blacklisted' || 
                record.action === 'blocked' || 
                record.status === 'blocked' ||
                record.is_blocked === true ||
                record.blocked === true) {
              blockedCount++;
              uniqueThreatIPsInRange.add(record.ip);
            }
          });
          this.todayThreats = uniqueThreatIPsInRange.size;
          this.autoBlockedCount = blockedCount;
        }
      } catch (error) {
        console.error('获取威胁情报自动封禁统计失败:', error);
        if (fetchType === 'timeRange') {
          this.todayThreats = 0;
          this.autoBlockedCount = 0;
        } else {
          this.totalThreatBlockedIPs = [];
        }
      }
    },

    async deleteWhite(id) {
      try {
        await axios.post('/api/delwhite', { id: id });
        this.showSuccess('白名单条目删除成功');
        this.fetchWhiteList();
      } catch (err) {
        console.error('删除白名单失败:', err);
        this.showError('删除白名单失败');
      }
    },

    async deleteBlack(ip) {
      try {
        // 假设后端删除黑名单需要IP
        await axios.post('/api/delblack', { ip: ip });
        this.showSuccess('黑名单条目删除成功');
        this.fetchBlackList();
        this.fetchBlockedIPs('all'); // 黑名单有变动，可能影响总的规则封禁IP统计
        this.fetchProtectionStats('all'); // 黑名单有变动，可能影响总的威胁情报封禁IP统计
      } catch (err) {
        console.error('删除黑名单失败:', err);
        this.showError('删除黑名单失败');
      }
    },

    async addWhite() {
      try {
        const payload = {
          name: this.newWhiteName,
          ip: this.newWhiteIP,
          remark: this.newWhiteRemark
        };
        await axios.post('/api/addwhite', payload);
        this.showSuccess('白名单添加成功');
        this.newWhiteName = '';
        this.newWhiteIP = '';
        this.newWhiteRemark = '';
        this.fetchWhiteList();
      } catch (err) {
        console.error('添加白名单失败:', err);
        this.showError('添加白名单失败');
      }
    },

    async addBlack() {
      try {
        const payload = {
          ip: this.newBlackIP,
          reason: this.newBlackReason,
          duration: this.newBlackDuration
        };
        await axios.post('/api/addblack', payload);
        this.showSuccess('黑名单添加成功');
        this.newBlackIP = '';
        this.newBlackReason = '恶意扫描';
        this.newBlackDuration = '24h';
        this.fetchBlackList();
        this.fetchBlockedIPs('all'); // 黑名单有变动，可能影响总的规则封禁IP统计
        this.fetchProtectionStats('all'); // 黑名单有变动，可能影响总的威胁情报封禁IP统计
      } catch (err) {
        console.error('添加黑名单失败:', err);
        this.showError('添加黑名单失败');
      }
    },

    async addToBlacklist(ip) {
      try {
        // 这通常是一个按钮点击操作，所以默认原因和时长
        await axios.post('/api/addblack', { ip: ip, reason: '手动拉黑', duration: 'permanent' });
        this.showSuccess(`IP ${ip} 已添加到黑名单`);
        this.fetchBlackList(); // 刷新黑名单列表
        this.fetchBlockedIPs('all'); // 刷新总统计
        this.fetchProtectionStats('all'); // 刷新总统计
      } catch (err) {
        console.error('手动添加到黑名单失败:', err);
        this.showError(`添加IP ${ip} 到黑名单失败`);
      }
    },

    async blockIP(ip) {
      try {
        // 高频请求的IP进行封禁，可以设置默认原因和时长
        await axios.post('/api/addblack', { ip: ip, reason: '高频请求', duration: '24h' });
        this.showSuccess(`IP ${ip} 已被封禁 (高频请求)`);
        this.fetchBlackList(); // 刷新黑名单列表
        this.fetchBlockedIPs('all'); // 刷新总统计
        this.fetchProtectionStats('all'); // 刷新总统计
      } catch (err) {
        console.error('封禁高频IP失败:', err);
        this.showError(`封禁IP ${ip} 失败`);
      }
    },

    getThreatLevelFromScore(score) {
      if (score === null || score === undefined) return 'unknown';
      if (score < -5) return 'high';
      if (score < 0) return 'medium';
      return 'low';
    },
  },
};
</script>

<style>
/* 在父组件的根样式中定义CSS变量 */
.waf-management {
  --fixed-card-height: 380px; /* 您可以在这里调整卡片的统一高度 */
  /* 其他全局或waf-management特定样式 */
  font-family: 'Inter', sans-serif;
  color: #fff;
  background-color: #0d1a26; /* 深色背景 */
  min-height: 100vh;
  padding: 1.5rem 2rem;
  box-sizing: border-box;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-left h1 {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #a0f0ed;
}

.header-subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
}

.refresh-btn {
  background-color: #667eea;
  color: white;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
}

.refresh-btn:hover {
  background-color: #5a67d8;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
}

.refresh-btn:disabled {
  background-color: #4a5568;
  cursor: not-allowed;
  transform: translateY(0);
  box-shadow: none;
  opacity: 0.7;
}

.monitoring-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); /* 适应性网格布局 */
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* 消息提示样式 */
.message {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  font-size: 0.95rem;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 1000;
}

.message.error {
  background-color: #e53e3e; /* 红色 */
  color: white;
}

.message.success {
  background-color: #38a169; /* 绿色 */
  color: white;
}

.message-icon {
  margin-right: 0.6rem;
  font-size: 1.2rem;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  margin-left: 1rem;
  cursor: pointer;
  line-height: 1;
  padding: 0 5px;
  opacity: 0.8;
}

.close-btn:hover {
  opacity: 1;
}

/* 消息过渡动画 */
.message-enter-active, .message-leave-active {
  transition: all 0.5s ease;
}
.message-enter-from, .message-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-30px);
}

/* 加载动画 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.mr-2 { margin-right: 0.5rem; }
.mr-1 { margin-right: 0.25rem; }

/* 其他 WAFManagementPanel 相关的样式，如果它们不在这个文件里，则不需要重复 */
/* 如果 WAFManagementPanel 的样式和 WAFMonitoringPanel, WAFAutoProtection 冲突，
   请确保 WAFManagementPanel 有自己独立的样式作用域或使用更具体的选择器。
   这里假定 WAFManagementPanel 是一个完全独立的组件，且其内部的卡片样式是独立的。
*/

@media (max-width: 768px) {
  .waf-management {
    padding: 1rem;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.8rem;
  }

  .header-left h1 {
    font-size: 1.8rem;
  }

  .header-subtitle {
    font-size: 0.9rem;
  }

  .refresh-btn {
    width: 100%;
    justify-content: center;
    padding: 0.7rem 1rem;
  }

  .monitoring-grid {
    grid-template-columns: 1fr; /* 小屏幕下堆叠显示 */
  }

  .message {
    width: calc(100% - 2rem);
    left: 1rem;
    transform: translateX(0);
  }
}
</style>