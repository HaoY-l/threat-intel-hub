<template>
  <div class="overview-section">
    <div class="overview-card" v-for="stat in statsOverview" :key="stat.key">
      <div class="stat-icon" :class="stat.iconClass">
        <i class="fa fa-2x" :class="stat.icon"></i>
      </div>
      <div class="stat-info">
        <div class="stat-title">{{ stat.title }}</div>
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-trend" :class="stat.trendClass">
          <i class="fa" :class="stat.trendIcon"></i> {{ stat.change }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WAFOverview',
  props: {
    statsOverview: {
      type: Array,
      required: true
    }
  }
}
</script>

<style scoped>
/* 统计概览 */
.overview-section {
  padding: 0 0 1.5rem 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.25rem;
}

.overview-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.bg-green-500 {
  background-color: #38a169;
}

.bg-red-500 {
  background-color: #e53e3e;
}

.bg-orange-500 {
  background-color: #ed8936;
}

.bg-blue-500 {
  background-color: #4299e1;
}
.bg-purple-500 {
  background-color: #8B5CF6; /* 这是 Tailwind CSS 的 purple-500 默认颜色，您可以根据喜好调整 */
}

.stat-info {
  flex: 1;
}

.stat-title {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.stat-trend {
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.text-green-500 {
  color: #38a169;
}

.text-red-500 {
  color: #e53e3e;
}
</style>