<template>
  <div 
    class="ai-chat-dialog-overlay" 
    @click.self="closeDialog" 
    role="dialog" 
    aria-modal="true" 
    aria-labelledby="chat-title"
  >
    <div class="ai-chat-dialog">
      <div class="chat-header">
        <div class="header-left">
          <span class="chat-title" id="chat-title">💬 AI 助手</span>
          <select 
            v-model="selectedModel" 
            @change="onModelChange" 
            class="model-selector"
            aria-label="选择 AI 模型"
          >
            <option v-for="model in availableModels" :key="model.id" :value="model.name">
              {{ model.name }}
            </option>
          </select>
        </div>
        <div class="header-right">
          <button @click="clearChat" class="icon-btn" title="清空对话" aria-label="清空对话" v-if="messages.length > 1">
            🗑️
          </button>
          <button @click="openModelManagement" class="icon-btn" title="模型管理" aria-label="打开模型管理">
            ⚙️
          </button>
          <button class="close-btn" @click="closeDialog" title="关闭对话框" aria-label="关闭对话框">×</button>
        </div>
      </div>
      
      <div class="chat-body" ref="chatBody" aria-live="polite">
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          class="message-container" 
          :class="{ 'user-message': message.sender === 'user' }"
        >
          <img 
            v-if="message.sender === 'user'" 
            src="/UserAvatar.svg" 
            alt="用户头像" 
            class="avatar user-avatar"
            aria-hidden="true"
          />
          <img 
            v-if="message.sender === 'ai'" 
            src="/AiRobot.svg" 
            alt="AI 机器人头像" 
            class="avatar ai-avatar"
            aria-hidden="true"
          />
          <div class="message-bubble" :aria-label="`${message.sender === 'user' ? '用户' : 'AI'} 消息`">
            <div class="message-text">{{ message.text }}</div>
            <div class="message-time" v-if="message.time">{{ message.time }}</div>
          </div>
        </div>
        
        <div v-if="isLoading" class="message-container">
          <img src="/AiRobot.svg" alt="AI 正在输入" class="avatar ai-avatar" />
          <div class="message-bubble loading" role="status" aria-label="AI 正在思考中">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chat-footer">
        <div class="input-wrapper">
          <textarea 
            v-model="userInput" 
            @keydown.enter.exact.prevent="sendMessage"
            placeholder="输入消息... (Enter发送, Shift+Enter换行)"
            rows="1"
            ref="textareaInput"
            aria-label="输入聊天消息"
          ></textarea>
          <button 
            @click="sendMessage" 
            :disabled="isLoading || !userInput.trim()"
            class="send-btn"
            title="发送消息"
            aria-label="发送消息"
          >
            <span v-if="!isLoading">➡️</span> <span v-else class="spinner">⏳</span>
          </button>
        </div>
        <div class="footer-hint">
          <span class="model-indicator">当前模型: **{{ selectedModel }}**</span>
          <span class="message-count">共 {{ messages.length - 1 }} 条对话</span>
        </div>
      </div>
    </div>
    
    <div 
      v-if="showModelManagement" 
      class="model-management-overlay" 
      @click.self="closeModelManagement" 
      role="dialog" 
      aria-modal="true" 
      aria-labelledby="model-management-title"
    >
      <div class="model-management-container" @click.stop>
        <div class="model-management-header">
          <h2 id="model-management-title">🤖 AI 模型管理</h2>
          <button class="close-management-btn" @click="closeModelManagement" aria-label="关闭模型管理">×</button>
        </div>
        <ModelManagement @model-updated="handleModelUpdated" />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ModelManagement from './ModelManagement.vue';

export default {
  name: 'AiChatDialog',
  components: {
    ModelManagement
  },
  data() {
    return {
      userInput: '',
      selectedModel: 'doubao',
      availableModels: [],
      messages: [
        { sender: 'ai', text: '你好！我是你的智能助手 👋 有什么可以帮你的吗？', time: this.getCurrentTime() }
      ],
      isLoading: false,
      showModelManagement: false
    };
  },
  async mounted() {
    await this.fetchAvailableModels();
    this.$nextTick(() => {
      this.$refs.textareaInput?.focus();
    });
  },
  methods: {
    closeDialog() {
      this.$emit('close-ai-dialog');
    },
    
    getCurrentTime() {
      const now = new Date();
      return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    },
    
    async fetchAvailableModels() {
      try {
        const response = await axios.get('/api/models');
        this.availableModels = response.data.models;
        if (this.availableModels.length > 0) {
          const doubaoModel = this.availableModels.find(m => m.name === 'doubao');
          if (doubaoModel) {
            this.selectedModel = 'doubao';
          } else {
            const activeModel = this.availableModels.find(m => m.is_active);
            if (activeModel) {
              this.selectedModel = activeModel.name;
            } else {
              this.selectedModel = this.availableModels[0].name;
            }
          }
        }
      } catch (error) {
        console.error('获取模型列表失败:', error);
      }
    },
    
    onModelChange() {
      const modelInfo = this.availableModels.find(m => m.name === this.selectedModel);
      if (modelInfo) {
        const switchMsg = { 
          sender: 'ai', 
          text: `✅ 已切换到 **${modelInfo.name}** 模型`,
          time: this.getCurrentTime()
        };
        this.messages.push(switchMsg);
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },
    
    async sendMessage() {
      if (!this.userInput.trim()) return;

      const userMessage = { 
        sender: 'user', 
        text: this.userInput,
        time: this.getCurrentTime()
      };
      this.messages.push(userMessage);
      this.isLoading = true;
      this.userInput = '';

      // 重置textarea高度并滚动
      this.$nextTick(() => {
        if (this.$refs.textareaInput) {
          this.$refs.textareaInput.style.height = 'auto';
        }
        this.scrollToBottom();
      });

      try {
        const response = await axios.post('/api/aichat', { 
          message: userMessage.text,
          model: this.selectedModel
        });
        const aiReply = { 
          sender: 'ai', 
          text: response.data.reply,
          time: this.getCurrentTime()
        };
        this.messages.push(aiReply);
      } catch (error) {
        console.error('AI对话请求失败:', error);
        // 优化错误信息
        const errorMessage = { 
          sender: 'ai', 
          text: '❌ 抱歉，AI助手请求失败，请检查网络或模型配置。',
          time: this.getCurrentTime()
        };
        this.messages.push(errorMessage);
      } finally {
        this.isLoading = false;
        this.$nextTick(() => {
          this.scrollToBottom();
          this.$refs.textareaInput?.focus();
        });
      }
    },
    
    scrollToBottom() {
      const chatBody = this.$refs.chatBody;
      if (chatBody) {
        // 优化: 使用 behavior: 'smooth' 实现平滑滚动
        chatBody.scrollTo({
          top: chatBody.scrollHeight,
          behavior: 'smooth'
        });
      }
    },
    
    clearChat() {
      if (confirm('⚠️ 确定要清空所有对话记录吗？此操作不可撤销。')) {
        this.messages = [
          { 
            sender: 'ai', 
            text: '✅ 对话已清空，我是你的智能助手 👋 让我们重新开始吧！',
            time: this.getCurrentTime()
          }
        ];
        this.$nextTick(() => {
          this.$refs.textareaInput?.focus();
        });
      }
    },
    
    openModelManagement() {
      this.showModelManagement = true;
    },
    
    closeModelManagement() {
      this.showModelManagement = false;
      this.fetchAvailableModels();
    },
    
    handleModelUpdated() {
      this.fetchAvailableModels();
    }
  },
  watch: {
    userInput() {
      this.$nextTick(() => {
        const textarea = this.$refs.textareaInput;
        if (textarea) {
          // 确保内容填满后才扩展，并限制最大高度
          textarea.style.height = 'auto';
          textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        }
      });
    }
  }
};
</script>

<style scoped>
/* 主容器 - 使用硬件加速 */
.ai-chat-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.15s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.ai-chat-dialog {
  width: 500px;
  height: 700px;
  background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
  overflow: hidden;
  animation: slideUp 0.2s ease-out;
  transform: translateZ(0);
  backface-visibility: hidden;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 头部 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #1e3a8a 0%, #1e293b 100%);
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.chat-title {
  font-weight: 600;
  font-size: 1.1rem;
  white-space: nowrap;
}

/* 优化 model-selector 的样式，提高可读性 */
.model-selector {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.4rem 2rem 0.4rem 0.8rem; /* 增加右侧内边距 */
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.15s;
  outline: none;
  max-width: 150px;
  
  /* 自定义下拉箭头 */
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="10" height="5" viewBox="0 0 10 5"><path d="M0 0l5 5 5-5z" fill="%23ffffff"/></svg>');
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 8px 5px;
}

.model-selector:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

.model-selector:focus {
  border-color: #60a5fa;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.icon-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #fff;
  font-size: 1.2rem;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.icon-btn:active {
  transform: scale(0.95);
}

.close-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 2rem;
  width: 36px;
  height: 36px;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  line-height: 1;
  flex-shrink: 0;
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  transform: rotate(90deg);
}

/* 聊天区域 */
.chat-body {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #0f172a;
}

.chat-body::-webkit-scrollbar {
  width: 6px;
}

.chat-body::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.chat-body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

.chat-body::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.message-container {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.user-message {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.message-bubble {
  max-width: 70%;
  padding: 0.875rem 1.125rem;
  border-radius: 16px;
  line-height: 1.5;
  word-wrap: break-word;
  color: #fff;
  font-size: 0.95rem;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.message-container:not(.user-message) .message-bubble {
  background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
  border-bottom-left-radius: 4px;
}

.user-message .message-bubble {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-bottom-right-radius: 4px;
}

.message-text {
  margin-bottom: 0.25rem;
}

.message-time {
  font-size: 0.7rem;
  opacity: 0.7;
  text-align: right;
  margin-top: 0.25rem;
}

/* 加载动画 */
.loading {
  background: linear-gradient(135deg, #334155 0%, #1e293b 100%) !important;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 0.25rem 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #60a5fa;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* 底部输入区 */
.chat-footer {
  padding: 1rem 1.5rem;
  background: #1e293b;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.input-wrapper textarea {
  flex: 1;
  padding: 0.875rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: #0f172a;
  color: #fff;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.15s, height 0.15s ease-out; /* 优化: 增加 height 过渡 */
  resize: none;
  min-height: 44px;
  max-height: 120px;
  font-family: inherit;
  line-height: 1.5;
}

.input-wrapper textarea:focus {
  border-color: #3b82f6;
}

.input-wrapper textarea::placeholder {
  color: #64748b;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #fff;
  cursor: pointer;
  /* 优化: 使用更活泼的过渡函数 */
  transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
  font-size: 1.5rem; /* 优化: 增大图标 */
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05); /* 优化: 轻微放大 */
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.5); /* 优化: 阴影更明显 */
}

.send-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.send-btn:disabled {
  background: #334155;
  cursor: not-allowed;
  opacity: 0.6;
  transform: none; /* 禁用时的状态重置 */
  box-shadow: none;
}

.spinner {
  display: inline-block;
  animation: spin 1s linear infinite;
  font-size: 1.25rem; /* 保持一致 */
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.footer-hint {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #64748b;
  padding: 0 0.25rem;
}

.model-indicator {
  font-weight: 500;
  color: #94a3b8; /* 稍亮一点 */
}

.message-count {
  opacity: 0.8;
}

/* 模型管理模态框 (Model Management Modal) */
.model-management-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000; /* Z-index: 2000，确保高于聊天主窗口 (1000) */
  backdrop-filter: blur(4px);
  animation: fadeIn 0.15s ease-out;
}

.model-management-container {
  background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);
  border-radius: 20px;
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
  animation: slideUp 0.2s ease-out;
  transform: translateZ(0);
}

.model-management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #1e3a8a 0%, #1e293b 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px 20px 0 0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.model-management-header h2 {
  color: #fff;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.close-management-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #fff;
  font-size: 2rem;
  cursor: pointer;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  transition: all 0.15s;
  line-height: 1;
}

.close-management-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  transform: rotate(90deg);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-chat-dialog {
    width: 95vw;
    height: 90vh;
  }
  
  .chat-header {
    padding: 0.875rem 1rem;
  }
  
  .chat-title {
    font-size: 1rem;
  }
  
  .model-selector {
    font-size: 0.85rem;
    padding: 0.35rem 1.75rem 0.35rem 0.7rem;
    max-width: 120px;
    background-position: right 0.6rem center;
  }
  
  .icon-btn, .close-btn {
    width: 32px;
    height: 32px;
    font-size: 1.1rem;
  }
  
  .close-btn {
    font-size: 1.75rem;
  }
  
  .chat-body {
    padding: 1rem;
  }
  
  .avatar {
    width: 36px;
    height: 36px;
  }
  
  .message-bubble {
    font-size: 0.9rem;
    padding: 0.75rem 1rem;
    max-width: 80%;
  }
  
  .chat-footer {
    padding: 0.875rem 1rem;
  }
  
  .footer-hint {
    font-size: 0.7rem;
  }

  .send-btn {
    width: 40px;
    height: 40px;
    font-size: 1.3rem;
  }

  .input-wrapper textarea {
    min-height: 40px;
  }
}
</style>