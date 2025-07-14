<template>
  <header class="header">
    <div class="container">
      <h1 class="logo">威胁情报仪表板</h1>
      <nav class="nav">
        <ul>
          <li><a href="#" class="nav-link">首页</a></li>
          <li><a href="#" class="nav-link">威胁情报</a></li>
          <li><a href="#" class="nav-link">CVE漏洞</a></li>
          <li><a href="#" class="nav-link">设置</a></li>
        </ul>
      </nav>
    </div>
  </header>
</template>

<script>
export default {
  name: 'Header'
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
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

.nav ul {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 2rem;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: white;
}

@media (max-width: 768px) {
  .container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav ul {
    gap: 1rem;
  }
}
</style>