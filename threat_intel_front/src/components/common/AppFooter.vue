<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-content">
        <div class="copyright">
          © 2025 CyberGuard. 网络安全威胁情报平台
        </div>
        <div class="system-info">
          <span class="info-item">API状态: {{ apiStatus }}</span>
          <span class="info-item">数据更新: {{ updateStatus }}</span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter',
  data() {
    return {
      apiStatus: '正常',
      updateStatus: '实时'
    }
  }
}
</script>

<style scoped>
.footer {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(139, 92, 246, 0.3);
  margin-top: 3rem;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 0;
}

.copyright {
  color: #9ca3af;
  font-size: 0.875rem;
}

.system-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.info-item {
  color: #a855f7;
  font-size: 0.875rem;
}

@media (max-width: 640px) {
  .footer-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .system-info {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
