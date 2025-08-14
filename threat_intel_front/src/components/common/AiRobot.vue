<template>
  <div class="ai-robot-container" @click="handleRobotClick">
    <div class="ai-robot-icon">
      <img src="/AiRobot.svg" alt="AI Robot Icon" class="icon-img" />
    </div>
    <div class="tooltip">我是AI机器人，需要什么帮助吗？</div>
  </div>
</template>

<script>
export default {
  name: 'AiRobot',
  methods: {
    handleRobotClick() {
      // 在这里添加弹出AI对话框的逻辑
      alert('AI对话框功能暂未开发，敬请期待！');
    }
  }
};
</script>

<style scoped>
.ai-robot-container {
  /* 保持与原组件相同的定位，确保不影响Header布局 */
  position: absolute;
  left: 21rem; 
  top: 50%;
  transform: translateY(-50%);
  z-index: 101;
  cursor: pointer;
  
  /* 添加跳动动画 */
  animation: bounce 2s infinite;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.ai-robot-icon {
  width: 40px;
  height: 40px;
  background-color: #5d92ff; /* 小蓝人背景色 */
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
}

.icon-img {
  width: 70%;
  height: 70%;
}

.tooltip {
  /* 提示语默认隐藏 */
  visibility: hidden;
  opacity: 0;
  
  /* 关键改动：使用flexbox和padding实现气泡效果 */
  display: flex;
  align-items: center;
  background-color: #3b4b60; /* 气泡背景色 */
  color: #fff;
  border-radius: 12px;
  padding: 0.75rem 1.25rem;
  position: relative;
  z-index: 1;
  
  /* 气泡的尖角 */
  &::before {
    content: '';
    position: absolute;
    top: 50%;
    right: 100%;
    transform: translateY(-50%);
    width: 0;
    height: 0;
    border-style: solid;
    border-width: 8px 8px 8px 0;
    border-color: transparent #3b4b60 transparent transparent;
  }
  
  /* 使用动画控制提示语的自动显示和隐藏 */
  animation: tooltip-fade 8s infinite;
}

/* 提示语的自动显示/隐藏动画 */
@keyframes tooltip-fade {
  0%   { visibility: hidden; opacity: 0; }
  10%  { visibility: visible; opacity: 1; }
  50%  { visibility: visible; opacity: 1; }
  60%  { visibility: hidden; opacity: 0; }
  100% { visibility: hidden; opacity: 0; }
}

/* 跳动动画 */
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(-50%);
  }
  40% {
    transform: translateY(-70%);
  }
  60% {
    transform: translateY(-40%);
  }
}

/* 媒体查询以适应不同屏幕大小 */
@media (max-width: 768px) {
  .ai-robot-container {
    left: auto;
    right: 1.5rem;
    top: 50%;
    transform: translateY(-50%);
    display: none; /* 在小屏幕上隐藏，避免与导航栏重叠 */
  }
}
</style>