<template>
  <div class="monitor-card auto-protection">
    <div class="card-header">
      <div class="card-title">
        <i class="card-icon fa fa-bolt"></i>
        <span>威胁情报自动封禁</span>
      </div>
      <div class="card-actions">
        <div class="status-indicator" :class="{ active: autoProtectionEnabled }"></div>
      </div>
    </div>
    <div class="card-content">
      <div class="protection-stats">
        <div class="protection-item">
          <div class="protection-label">威胁情报检测</div>
          <div class="protection-status" :class="{ active: threatIntelligenceEnabled }">
            <span class="status-dot"></span>
            {{ threatIntelligenceEnabled ? '已启用' : '已禁用' }}
          </div>
        </div>
        <div class="protection-item">
          <div class="protection-label">自动封禁</div>
          <div class="protection-status" :class="{ active: autoBlockEnabled }">
            <span class="status-dot"></span>
            {{ autoBlockEnabled ? '已启用' : '已禁用' }}
          </div>
        </div>
        <div class="protection-item">
          <div class="protection-label">智能学习</div>
          <div class="protection-status" :class="{ active: aiLearningEnabled }">
            <span class="status-dot"></span>
            {{ aiLearningEnabled ? '运行中' : '已暂停' }}
          </div>
        </div>
      </div>
      
      <div class="auto-stats">
        <div class="auto-stat-item">
          <div class="stat-number">{{ autoBlockedCount }}</div>
          <div class="stat-label">今日自动封禁</div>
        </div>
        <div class="auto-stat-item">
          <div class="stat-number">{{ todayThreats }}</div>
          <div class="stat-label">今日威胁拦截</div>
        </div>
      </div>
      
      <div class="threat-trend mt-4">
        <div class="trend-header">
          <h4>威胁趋势</h4>
          <span class="time-range">(今日)</span>
        </div>
        <div class="trend-chart">
          <div ref="trendChart" class="chart-container"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'WAFAutoProtection',
  props: {
    autoProtectionEnabled: {
      type: Boolean,
      default: true
    },
    threatIntelligenceEnabled: {
      type: Boolean,
      default: true
    },
    autoBlockEnabled: {
      type: Boolean,
      default: true
    },
    aiLearningEnabled: {
      type: Boolean,
      default: true
    },
    autoBlockedCount: {
      type: Number,
      default: 0
    },
    todayThreats: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      trendChart: null
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart()
    })
  },
  beforeDestroy() {
    if (this.trendChart) {
      this.trendChart.dispose()
    }
  },
  methods: {
    initChart() {
      const chartDom = this.$refs.trendChart
      this.trendChart = echarts.init(chartDom)
      
      const option = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          textStyle: {
            color: '#333'
          },
          axisPointer: {
            type: 'cross',
            crossStyle: {
              color: '#999'
            }
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'],
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.7)'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.2)'
            }
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: 'rgba(255, 255, 255, 0.7)'
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.2)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          }
        },
        series: [
          {
            name: '攻击尝试',
            type: 'line',
            data: [320, 332, 301, 334, 390, 330, 320, 350],
            areaStyle: {
              color: 'rgba(102, 126, 234, 0.3)'
            },
            itemStyle: {
              color: '#667eea'
            }
          },
          {
            name: '成功拦截',
            type: 'line',
            data: [220, 182, 191, 234, 290, 330, 310, 340],
            areaStyle: {
              color: 'rgba(56, 161, 105, 0.3)'
            },
            itemStyle: {
              color: '#38a169'
            }
          }
        ]
      }
      
      this.trendChart.setOption(option)
      
      // 监听窗口大小变化，调整图表
      window.addEventListener('resize', () => {
        this.trendChart.resize()
      })
    }
  }
}
</script>

<style scoped>
.monitor-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.monitor-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.card-header {
  padding: 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.1);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.card-icon {
  font-size: 1.2rem;
}

.time-range {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.card-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

/* 自动防护状态面板 */
.protection-stats {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.protection-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  padding: 0.5rem 0;
}

.protection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  user-select: none;
}

.protection-status.active {
  color: #38a169;
}

.status-dot {
  width: 10px;
  height: 10px;
  background: #38a169;
  border-radius: 50%;
  display: inline-block;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #e53e3e;
  transition: all 0.3s ease;
}

.status-indicator.active {
  background: #38a169;
  box-shadow: 0 0 8px rgba(56, 161, 105, 0.5);
}

/* 自动统计数字 */
.auto-stats {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.auto-stat-item {
  text-align: center;
}

.stat-number {
  font-size: 1.75rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
}

/* 威胁趋势图表 */
.trend-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.trend-header h4 {
  margin: 0;
  font-weight: 600;
  font-size: 0.9rem;
}

.chart-container {
  height: 180px;
  width: 100%;
}
</style>