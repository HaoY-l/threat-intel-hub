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
      // 触发一个事件，通知父组件显示AI对话框
      this.$emit('show-ai-dialog');
    }
  }
};
</script>

<style scoped>
.ai-robot-container {
  position: absolute;
  left: 21rem; 
  top: 50%;
  transform: translateY(-50%);
  z-index: 101;
  cursor: pointer;
  animation: bounce 2s infinite;
  display: flex;
  align-items: center;
  gap: 1rem;
}
.ai-robot-icon {
  width: 40px;
  height: 40px;
  background-color: #5d92ff;
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
  visibility: hidden;
  opacity: 0;
  display: flex;
  align-items: center;
  background-color: #3b4b60;
  color: #fff;
  border-radius: 12px;
  padding: 0.75rem 1.25rem;
  position: relative;
  z-index: 1;
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
  animation: tooltip-fade 8s infinite;
}
@keyframes tooltip-fade {
  0% { visibility: hidden; opacity: 0; }
  10% { visibility: visible; opacity: 1; }
  50% { visibility: visible; opacity: 1; }
  60% { visibility: hidden; opacity: 0; }
  100% { visibility: hidden; opacity: 0; }
}
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(-50%); }
  40% { transform: translateY(-70%); }
  60% { transform: translateY(-40%); }
}
@media (max-width: 768px) {
  .ai-robot-container {
    left: auto;
    right: 1.5rem;
    top: 50%;
    transform: translateY(-50%);
    display: none;
  }
}
</style>