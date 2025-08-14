<template>
  <div class="ai-chat-dialog-overlay" @click.self="closeDialog">
    <div class="ai-chat-dialog">
      <div class="chat-header">
        <span class="chat-title">AI 助手</span>
        <button class="close-btn" @click="closeDialog">×</button>
      </div>
      <div class="chat-body">
        <div v-for="(message, index) in messages" :key="index" class="message-container" :class="{ 'user-message': message.sender === 'user' }">
          <img v-if="message.sender === 'user'" src="/UserAvatar.svg" alt="User Avatar" class="avatar user-avatar" />
          <img v-if="message.sender === 'ai'" src="/AiRobot.svg" alt="AI Avatar" class="avatar ai-avatar" />
          <div class="message-bubble">
            {{ message.text }}
          </div>
        </div>
        <div v-if="isLoading" class="message-container">
          <img src="/AiRobot.svg" alt="AI Avatar" class="avatar ai-avatar" />
          <div class="message-bubble loading">...</div>
        </div>
      </div>
      <div class="chat-footer">
        <input v-model="userInput" @keyup.enter="sendMessage" placeholder="请输入你的问题..." />
        <button @click="sendMessage" :disabled="isLoading">发送</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AiChatDialog',
  data() {
    return {
      userInput: '',
      messages: [
        { sender: 'ai', text: '你好，我是你的智能助手，有什么可以帮你的吗？' }
      ],
      isLoading: false
    };
  },
  methods: {
    closeDialog() {
      this.$emit('close-ai-dialog');
    },
    async sendMessage() {
      if (!this.userInput.trim()) return;

      const userMessage = { sender: 'user', text: this.userInput };
      this.messages.push(userMessage);
      this.isLoading = true;
      this.userInput = '';

      try {
        const response = await axios.post('/api/aichat', { message: userMessage.text });
        const aiReply = { sender: 'ai', text: response.data.reply };
        this.messages.push(aiReply);
      } catch (error) {
        console.error('AI对话请求失败:', error);
        const errorMessage = { sender: 'ai', text: '抱歉，AI助手暂时无法回复，请稍后再试。' };
        this.messages.push(errorMessage);
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.ai-chat-dialog-overlay {
  /* 强制全屏覆盖，并使用flexbox居中 */
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw; /* 确保宽度是视口宽度 */
  height: 100vh; /* 确保高度是视口高度 */
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.ai-chat-dialog {
  width: 450px; /* 稍微增加宽度 */
  height: 650px; /* 稍微增加高度 */
  background: #1e293b;
  border-radius: 1.5rem; /* 增加圆角 */
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6); /* 更深的阴影 */
  overflow: hidden;
  transform: scale(1);
  transition: transform 0.3s ease-in-out;
}
.ai-chat-dialog:hover {
  transform: scale(1.01);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 2rem;
  background: #101729;
  color: #fff;
  border-bottom: 1px solid #3c4a60;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.75rem;
  cursor: pointer;
  transition: transform 0.2s;
}
.close-btn:hover {
  transform: rotate(90deg) scale(1.2);
}

.chat-body {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background: #1e293b;
}

.message-container {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.user-message {
  flex-direction: row-reverse;
}

.avatar {
  width: 48px; /* 增加头像大小 */
  height: 48px;
  border-radius: 50%;
  flex-shrink: 0;
  object-fit: cover;
  border: 3px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.message-bubble {
  max-width: 75%;
  padding: 1rem 1.25rem;
  border-radius: 1.5rem; /* 增加气泡圆角 */
  line-height: 1.6;
  word-wrap: break-word;
  color: #fff;
  font-size: 1rem;
  position: relative;
  transition: transform 0.2s ease;
}

.message-container:not(.user-message) .message-bubble {
  background: #3b4b60;
  border-bottom-left-radius: 0.5rem;
}

.user-message .message-bubble {
  background: #5d92ff;
  border-bottom-right-radius: 0.5rem;
}
.message-bubble:hover {
  transform: translateY(-2px);
}

.loading {
  font-style: italic;
  color: #94a3b8;
  animation: pulse 1.5s infinite ease-in-out;
}

.chat-footer {
  display: flex;
  padding: 1.5rem;
  background: #101729;
  border-top: 1px solid #3c4a60;
  gap: 1rem;
}

.chat-footer input {
  flex: 1;
  padding: 0.85rem 1.25rem;
  border-radius: 0.75rem;
  border: 1px solid #475569;
  background: #1e293b;
  color: #fff;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
}

.chat-footer input:focus {
  border-color: #5d92ff;
}

.chat-footer button {
  padding: 0.85rem 2rem;
  border-radius: 0.75rem;
  border: none;
  background: #5d92ff;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s ease;
}

.chat-footer button:hover {
  background: #4779ff;
}

.chat-footer button:disabled {
  background: #475569;
  cursor: not-allowed;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>