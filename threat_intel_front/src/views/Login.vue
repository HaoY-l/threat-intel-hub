<template>
  <div class="login-page">
    <!-- 背景装饰层 -->
    <div class="login-bg"></div>
    <!-- 主内容区 -->
    <div class="login-container">
      <!-- 左侧可视化区域 -->
      <div class="login-visual">
        <div class="visual-icon">
          <svg viewBox="0 0 100 100" width="80" height="80">
            <path d="M20,20 L80,20 L80,80 L20,80 Z" fill="rgba(255,255,255,0.1)" stroke="rgba(0,212,255,0.5)" stroke-width="2"/>
            <path d="M30,30 L70,30 L70,40 L30,40 Z" fill="rgba(0,212,255,0.3)"/>
            <path d="M30,50 L70,50 L70,60 L30,60 Z" fill="rgba(0,212,255,0.3)"/>
            <path d="M30,70 L70,70 L70,80 L30,80 Z" fill="rgba(0,212,255,0.3)"/>
            <path d="M10,40 L20,40 L20,60 L10,60 Z" fill="rgba(255,107,157,0.3)"/>
          </svg>
        </div>
        <div class="visual-title">威胁协同平台</div>
        <div class="visual-desc">企业安全 · 威胁情报 · 协同防御</div>
      </div>
      <!-- 右侧登录表单区 -->
      <div class="login-card">
        <!-- 项目Logo + 标题 -->
        <div class="card-header">
          <div class="logo">
            <span class="logo-dot"></span>
            <span class="logo-dot"></span>
            <span class="logo-dot"></span>
          </div>
          <div class="card-title">Threat Intel Hub</div>
        </div>
        <!-- 账号输入框 -->
        <el-input 
          v-model="loginForm.username" 
          placeholder="请输入账号" 
          prefix-icon="el-icon-user"
          :disabled="isLoading"
          class="input-item"
        ></el-input>
        <!-- 密码输入框 -->
        <el-input 
          v-model="loginForm.password" 
          type="password" 
          placeholder="请输入密码" 
          prefix-icon="el-icon-lock"
          :disabled="isLoading"
          class="input-item"
        ></el-input>
        <!-- 错误提示 -->
        <div class="error-message" v-if="errorMsg">{{ errorMsg }}</div>
        <!-- 登录按钮 -->
        <el-button 
          type="primary" 
          @click="handleLogin" 
          :loading="isLoading"
          class="login-btn"
        >
          登录
        </el-button>

        <!-- 默认账号提示 -->
        <div class="login-tip">
          默认账号：threatintel | 密码：threatintel<br>
          首次登录后请修改密码！！！
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';

const emit = defineEmits(['login-success']);

const loginForm = ref({
  username: '',
  password: ''
});
const isLoading = ref(false);
const errorMsg = ref('');

const handleLogin = async () => {
  if (!loginForm.value.username.trim() || !loginForm.value.password.trim()) {
    errorMsg.value = '用户名和密码不能为空';
    return;
  }
  errorMsg.value = '';
  isLoading.value = true;

  try {
    const res = await axios.post(
      '/api/auth/login',
      loginForm.value,
      { headers: { 'Content-Type': 'application/json' } }
    );

    const { status, data, message } = res.data;
    if (status === 'success' && data) {
      localStorage.setItem('user', JSON.stringify(data));
      emit('login-success', data);
      ElMessage.success(message || '登录成功！');
    } else {
      errorMsg.value = message || '登录失败，请检查账号密码';
    }
  } catch (err) {
    console.error('登录异常：', err);
    const errMsg = err.response?.data?.message || '网络异常或服务器错误，请稍后重试';
    errorMsg.value = errMsg;
    ElMessage.error(errMsg);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* 页面整体布局 - 全屏铺满 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
.login-page {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  position: relative;
  background-color: #0f0f23;
}
/* 背景装饰 - 自适应铺满 */
.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  /* background: url('@/assets/login-bg.png') no-repeat center; */
  background-size: cover; /* 背景图自适应屏幕，保持比例 */
  opacity: 0.15;
}
/* 主内容容器 - 自适应屏幕，居中显示 */
.login-container {
  /* 用min/max-width限制范围，避免过宽或过窄 */
  width: 100%;
  max-width: 900px;
  min-width: 320px;
  /* 高度自适应，基于屏幕比例 */
  height: auto;
  min-height: 450px;
  max-height: 550px;
  /* 居中定位，随窗口移动 */
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 1;
}
/* 左侧可视化区域 - 自适应占比 */
.login-visual {
  flex: 1;
  min-width: 280px; /* 最小宽度，避免挤压 */
  background: linear-gradient(135deg, #0f172a, #1e293b);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  color: #fff;
}
.visual-icon {
  margin-bottom: 1.5rem;
  /* 图标自适应大小 */
  transform: scale(clamp(0.8, calc(100vw / 1000), 1));
}
.visual-title {
  font-size: clamp(1.4rem, calc(100vw / 60), 1.8rem); /* 自适应字体 */
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.visual-desc {
  color: rgba(255, 255, 255, 0.7);
  font-size: clamp(0.9rem, calc(100vw / 80), 1rem); /* 自适应字体 */
}
/* 右侧登录卡片 - 自适应占比 */
.login-card {
  flex: 1;
  min-width: 280px; /* 最小宽度，避免挤压 */
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  padding: clamp(1.5rem, calc(100vw / 50), 2.5rem); /* 自适应内边距 */
  display: flex;
  flex-direction: column;
  justify-content: center;
}
/* 卡片头部（Logo+标题） */
.card-header {
  margin-bottom: clamp(1.5rem, calc(100vw / 50), 2rem); /* 自适应间距 */
  text-align: center;
}
.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}
.logo-dot {
  display: inline-block;
  width: clamp(10px, calc(100vw / 80), 12px); /* 自适应圆点大小 */
  height: clamp(10px, calc(100vw / 80), 12px);
  border-radius: 50%;
  background: #ff6b9d;
  margin-right: 4px;
}
.logo-dot:nth-child(2) {
  background: #00d4ff;
}
.logo-dot:nth-child(3) {
  background: #facc15;
}
.logo-text {
  font-size: clamp(1.2rem, calc(100vw / 65), 1.5rem); /* 自适应字体 */
  font-weight: 700;
  color: #fff;
  margin-left: 8px;
}
.card-title {
  color: rgba(255, 255, 255, 0.9);
  font-size: clamp(1rem, calc(100vw / 75), 1.2rem); /* 自适应字体 */
  font-weight: 500;
}
/* 输入框样式 - 自适应间距 */
.input-item {
  margin-bottom: clamp(1rem, calc(100vw / 70), 1.2rem);
}
/* 错误提示 */
.error-message {
  color: #ff4d4f;
  font-size: 0.875rem;
  margin: 0.5rem 0;
  height: 1.2rem;
}
/* 登录按钮 - 自适应样式 */
.login-btn {
  width: 100%;
  padding: clamp(0.7rem, calc(100vw / 100), 0.8rem) 0; /* 自适应内边距 */
  font-size: clamp(0.9rem, calc(100vw / 85), 1rem); /* 自适应字体 */
  background: linear-gradient(90deg, #00d4ff, #ff6b9d);
  border: none;
}
/* 卡片底部链接 */
.card-footer {
  display: flex;
  justify-content: space-between;
  margin-top: clamp(0.8rem, calc(100vw / 90), 1rem); /* 自适应间距 */
}
.footer-link {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
  cursor: pointer;
  text-decoration: none;
}
.footer-link:hover {
  color: #00d4ff;
}
/* 默认账号提示 */
.login-tip {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
  margin-top: clamp(1rem, calc(100vw / 80), 1.5rem); /* 自适应间距 */
}
/* Element Plus 组件适配 - 自适应输入框 */
::v-deep(.el-input__wrapper) {
  background-color: rgba(255, 255, 255, 0.05) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
}
::v-deep(.el-input__inner) {
  color: #fff !important;
  font-size: clamp(0.9rem, calc(100vw / 85), 1rem) !important; /* 自适应输入框字体 */
}
::v-deep(.el-input__placeholder) {
  color: #ccc !important;
}
::v-deep(.el-icon-user),
::v-deep(.el-icon-lock) {
  color: #ccc !important;
}
/* 响应式调整：小屏幕（平板/手机）隐藏左侧可视化区域 */
@media (max-width: 768px) {
  .login-visual {
    display: none;
  }
  .login-card {
    min-height: 420px;
  }
}
/* 响应式调整：超小屏幕（手机）优化内边距 */
@media (max-width: 375px) {
  .login-container {
    min-height: 380px;
    padding: 0.5rem;
  }
  .login-card {
    padding: 1.2rem;
  }
}
</style>