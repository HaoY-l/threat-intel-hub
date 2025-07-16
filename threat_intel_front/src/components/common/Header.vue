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
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #fff;
  margin: 0;
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
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.nav-link.active {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}
</style>
