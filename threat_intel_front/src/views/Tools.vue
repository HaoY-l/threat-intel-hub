<template>
  <div class="tools-page">
    <h1>我的工具箱</h1>
    <div class="card-container">
      <WeChatPublisherCard />
      <IpQueryCard />
    </div>
  </div>
</template>

<script>
// 导入工具卡片组件，路径已根据你的要求调整
import WeChatPublisherCard from '@/components/tools/WeChatPublisherCard.vue'
import IpQueryCard from '@/components/tools/IpQueryCard.vue'

export default {
  name: 'Tools', // 保持组件名为Tools
  components: {
    WeChatPublisherCard,
    IpQueryCard
  }
}
</script>

<style scoped>
.tools-page {
  padding: 2rem;
  background-color: #1e1e2f;
  min-height: 100vh;
  color: #fff;
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: #4caf50;
}

.card-container {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem; /* 卡片之间的间距 */
  justify-content: center;
}
</style>