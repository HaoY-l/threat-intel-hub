<template>
  <header class="header">
    <div class="container" style="width: 100% !important; max-width: none !important; margin: 0 !important; padding: 0 1.5rem !important; display: flex !important; justify-content: flex-start !important; align-items: center !important;">
      <div class="left-section" style="display: flex !important; align-items: center !important;">
        <h1 class="logo" style="margin: 0 !important; text-align: left !important; font-size: 1.5rem !important; position: absolute !important; left: 1.5rem !important; font-weight: bold !important; top: 50% !important; transform: translateY(-50%) !important; background: linear-gradient(135deg, #00d4ff, #ff6b9d, #c471ed) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; background-clip: text !important; text-shadow: 0 0 20px rgba(0, 212, 255, 0.5) !important;">
          🛡️ 威胁情报仪表板 🔍
        </h1>
        <AiRobot @show-ai-dialog="isChatDialogVisible = true" />
      </div>
      <div class="right-section" style="display: flex !important; align-items: center !important; margin-left: auto !important; position: absolute !important; right: 1.5rem !important; top: 50% !important; transform: translateY(-50%) !important;">
        <nav class="nav">
          <ul style="display: flex !important; gap: 2rem !important; margin: 0 !important; padding: 0 !important; list-style: none !important;">
            <li>
              <a
                href="#"
                class="nav-link"
                :class="{ active: active === 'threat' }"
                @click.prevent="setActiveTab('threat')"
              >威胁情报🚨</a>
            </li>
            <li>
              <a
                href="#"
                class="nav-link"
                :class="{ active: active === 'waf' }"
                @click.prevent="setActiveTab('waf')"
              >WAF协同🚀</a>
            </li>
            <li>
              <a
                href="#"
                class="nav-link"
                :class="{ active: active === 'tools' }"
                @click.prevent="setActiveTab('tools')"
              >工具箱🧰</a>
            </li>
          </ul>
        </nav>
      </div>
    </div>
    <AiChatDialog v-if="isChatDialogVisible" @close-ai-dialog="isChatDialogVisible = false" />
  </header>
</template>

<script>
// 1. 导入 AiRobot 和 AiChatDialog 组件
import AiRobot from '../../aichat/AiRobot.vue';
import AiChatDialog from '../../aichat/AiChatDialog.vue';

export default {
  name: 'Header',
  // 2. 注册 AiRobot 组件
  components: {
    AiRobot,
    AiChatDialog
  },
  props: {
    active: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      isChatDialogVisible: false
    };
  },
  methods: {
    setActiveTab(tab) {
      this.$emit('tab-change', tab);
    }
  }
}
</script>

<style scoped>
/* 你的原有样式保持不变 */
.header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
  position: relative;
  min-height: 80px;
}
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.left-section {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
}
.right-section {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  margin-left: auto;
}
.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #fff;
  margin: 0;
  text-align: left;
}
.nav ul {
  list-style: none;
  display: flex;
  gap: 2rem;
  margin: 0;
  padding: 0;
}
.nav-link {
  color: #fff;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  white-space: nowrap;
}
.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}
.nav-link.active {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}
@media (max-width: 768px) {
  .container {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
    padding: 0.8rem 1rem;
  }
  .left-section {
    justify-content: center;
    width: 100%;
  }
  .right-section {
    justify-content: center;
    width: 100%;
    margin-left: 0;
  }
  .logo {
    text-align: center;
    font-size: 1.3rem;
  }
  .nav ul {
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
  }
  .nav-link {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
}
@media (max-width: 480px) {
  .logo {
    font-size: 1.2rem;
  }
  .nav ul {
    gap: 0.8rem;
  }
  .nav-link {
    padding: 0.3rem 0.6rem;
    font-size: 0.85rem;
  }
}
</style>