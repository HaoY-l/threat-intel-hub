<template>
  <header class="header">
    <div class="container">
      <h1 class="logo">威胁情报仪表板</h1>
      <nav class="nav">
        <ul>
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
  </header>
</template>

<script>
export default {
  name: 'Header',
  props: {
    active: {
      type: String,
      required: true
    }
  },
  methods: {
    setActiveTab(tab) {
      this.$emit('tab-change', tab);
    }
  }
}
</script>

<style scoped>
.header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  justify-content: space-between; /* 将子元素（Logo 和 Nav）推向两端 */
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #fff;
  margin: 0;
}

.nav {
  /* 这些注释是可选的，因为它们描述的是默认行为或通过其他属性实现的布局 */
  /* 如果确实需要保留这些提示，请使用单行注释风格，或在外部编辑器中以非CSS方式注释 */
}

.nav ul {
  list-style: none;
  display: flex; /* 确保 li 元素水平排列 */
  gap: 2rem; /* 控制菜单项之间的间距 */
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
  white-space: nowrap; /* 防止菜单项在小屏幕下换行 */
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.nav-link.active {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

/* 媒体查询：响应式调整 */
@media (max-width: 768px) {
  .container {
    flex-direction: column; /* 小屏幕下堆叠显示 */
    align-items: flex-start; /* 左对齐 */
    gap: 1rem;
    padding: 0.8rem 1rem;
  }

  .logo {
    width: 100%; /* Logo占据整行 */
    text-align: center; /* Logo居中 */
    font-size: 1.3rem;
  }

  .nav {
    width: 100%; /* 导航占据整行 */
  }

  .nav ul {
    flex-wrap: wrap; /* 菜单项允许换行 */
    justify-content: center; /* 菜单项居中 */
    gap: 1rem; /* 减小间距 */
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