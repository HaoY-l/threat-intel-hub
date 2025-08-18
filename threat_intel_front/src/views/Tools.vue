<template>
  <div class="tools-page">
    <h1>我的工具箱</h1>
    <div class="card-container">
      <WeChatPublisherCard />
      <IpQueryCard />
      <DomainWhoisCard />
      <WafBlockIpCard />
    </div>
  </div>
</template>

<script>
import WeChatPublisherCard from '@/components/tools/WeChatPublisherCard.vue'
import IpQueryCard from '@/components/tools/IpQueryCard.vue'
import DomainWhoisCard from '@/components/tools/DomainWhoisCard.vue'
import WafBlockIpCard from '@/components/tools/WafBlockIpCard.vue'

export default {
  name: 'Tools',
  components: {
    WeChatPublisherCard,
    IpQueryCard,
    DomainWhoisCard,
    WafBlockIpCard
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
  gap: 2rem;
  justify-content: center;
}
</style>