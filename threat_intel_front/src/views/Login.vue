<template>
  <div class="login-container">
    <div class="login-card">
      <h2>威胁协同平台 - 登录</h2>
      <!-- 账号输入框 -->
      <el-input 
        v-model="loginForm.username" 
        placeholder="请输入用户名" 
        prefix-icon="el-icon-user"
        :disabled="isLoading"
      ></el-input>
      <!-- 密码输入框 -->
      <el-input 
        v-model="loginForm.password" 
        type="password" 
        placeholder="请输入密码" 
        prefix-icon="el-icon-lock"
        :disabled="isLoading"
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
        默认账号：threatintel | 密码：threatintel
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
// 移除 Vue Router 相关导入（useRouter）
import axios from 'axios';
import { ElMessage } from 'element-plus';

// 定义登录成功事件（传递给父组件 App.vue）
const emit = defineEmits(['login-success']);

// 表单数据
const loginForm = ref({
  username: '',
  password: ''
});
const isLoading = ref(false); // 登录加载状态
const errorMsg = ref(''); // 错误提示信息

// 登录核心逻辑
const handleLogin = async () => {
  // 1. 表单基础校验
  if (!loginForm.value.username.trim() || !loginForm.value.password.trim()) {
    errorMsg.value = '用户名和密码不能为空';
    return;
  }
  errorMsg.value = ''; // 清空之前的错误提示
  isLoading.value = true; // 开始加载

  try {
    // 2. 调用后端登录接口（适配 auth.py 返回格式）
    const res = await axios.post(
      '/api/auth/login', // 后端登录接口路径
      loginForm.value, // 请求参数（用户名+密码）
      {
        headers: {
          'Content-Type': 'application/json' // 明确请求格式
        }
      }
    );

    // 3. 处理后端响应
    const { status, data, message } = res.data;
    if (status === 'success' && data) {
      // 登录成功：存储用户信息到本地存储（维持登录状态）
      localStorage.setItem('user', JSON.stringify(data));
      // 触发事件，通知 App.vue 切换到功能页
      emit('login-success', data);
      // 提示登录成功
      ElMessage.success(message || '登录成功！');
    } else {
      // 登录失败（用户名/密码错误等）
      errorMsg.value = message || '登录失败，请检查账号密码';
    }
  } catch (err) {
    // 4. 异常处理（网络错误、后端500等）
    console.error('登录异常：', err);
    const errMsg = err.response?.data?.message || '网络异常或服务器错误，请稍后重试';
    errorMsg.value = errMsg;
    ElMessage.error(errMsg);
  } finally {
    // 5. 结束加载状态（无论成功失败）
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* 保持原有样式，新增深色主题适配和提示样式 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #0f0f23; /* 与项目深色主题一致 */
}
.login-card {
  width: 400px;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05); /* 半透明深色卡片 */
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
/* 标题样式（适配深色主题） */
.login-card h2 {
  text-align: center;
  color: #fff;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, #00d4ff, #ff6b9d);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.login-btn {
  width: 100%;
  margin-top: 1rem;
}
.error-message {
  color: #ff4d4f;
  font-size: 0.875rem;
  margin: 0.5rem 0;
  height: 1.2rem; /* 固定高度，避免页面抖动 */
}
/* 默认账号提示样式 */
.login-tip {
  text-align: center;
  color: #999;
  font-size: 0.875rem;
  margin-top: 1rem;
}
/* Element Plus 输入框适配深色主题 */
::v-deep(.el-input__wrapper) {
  background-color: rgba(255, 255, 255, 0.05) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
}
::v-deep(.el-input__inner) {
  color: #fff !important;
}
::v-deep(.el-input__placeholder) {
  color: #ccc !important;
}
::v-deep(.el-icon-user),
::v-deep(.el-icon-lock) {
  color: #ccc !important;
}
</style>