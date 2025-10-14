<!-- AiChatDialog.vue -->
<template>
  <div class="ai-chat-dialog-overlay" @click.self="closeDialog">
    <div class="ai-chat-dialog">
      <div class="chat-header">
        <span class="chat-title">AI 助手</span>
        <select v-model="selectedModel" @change="onModelChange" class="model-selector">
          <option v-for="model in availableModels" :key="model.id" :value="model.name">
            {{ model.name }}
          </option>
        </select>
        <button @click="openModelManagement" class="manage-models-btn" title="模型管理">
          🤖 模型管理
        </button>
        <button class="close-btn" @click="closeDialog">×</button>
      </div>
      <div class="chat-body" ref="chatBody">
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
    
    <!-- 模型管理模态框 -->
    <div v-if="showModelManagement" class="model-management-overlay" @click.self="closeModelManagement">
      <div class="model-management-container" @click.stop>
        <div class="model-management-header">
          <h2>🤖 AI 模型管理</h2>
          <button class="close-management-btn" @click="closeModelManagement">×</button>
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
      selectedModel: 'doubao', // 默认模型
      availableModels: [],     // 可用模型列表
      messages: [
        { sender: 'ai', text: '你好，我是你的智能助手，有什么可以帮你的吗？' }
      ],
      isLoading: false,
      showModelManagement: false
    };
  },
  async mounted() {
    // 组件加载时获取可用模型列表
    await this.fetchAvailableModels();
  },
  methods: {
    closeDialog() {
      this.$emit('close-ai-dialog');
    },
    
    async fetchAvailableModels() {
      try {
        const response = await axios.get('/api/models');
        this.availableModels = response.data.models;
        // 设置默认模型为第一个可用模型（如果没有默认的doubao）
        if (this.availableModels.length > 0) {
          // 如果有doubao模型，使用它作为默认模型
          const doubaoModel = this.availableModels.find(m => m.name === 'doubao');
          if (doubaoModel) {
            this.selectedModel = 'doubao';
          } else {
            // 否则使用第一个启用的模型
            const activeModel = this.availableModels.find(m => m.is_active);
            if (activeModel) {
              this.selectedModel = activeModel.name;
            } else {
              // 如果没有启用的模型，使用第一个模型
              this.selectedModel = this.availableModels[0].name;
            }
          }
        }
      } catch (error) {
        console.error('获取模型列表失败:', error);
        // 出错时保留默认模型
      }
    },
    
    onModelChange() {
      const modelInfo = this.availableModels.find(m => m.name === this.selectedModel);
      if (modelInfo) {
        const switchMsg = { 
          sender: 'ai', 
          text: `已切换到 ${modelInfo.name} 模型。` 
        };
        this.messages.push(switchMsg);
      }
    },
    
    async sendMessage() {
      if (!this.userInput.trim()) return;

      const userMessage = { sender: 'user', text: this.userInput };
      this.messages.push(userMessage);
      this.isLoading = true;
      this.userInput = '';

      // 滚动到最新的消息
      this.$nextTick(() => {
        this.scrollToBottom();
      });

      try {
        // 发送消息时携带模型信息
        const response = await axios.post('/api/aichat', { 
          message: userMessage.text,
          model: this.selectedModel  // 添加模型参数
        });
        const aiReply = { sender: 'ai', text: response.data.reply };
        this.messages.push(aiReply);
      } catch (error) {
        console.error('AI对话请求失败:', error);
        const errorMessage = { sender: 'ai', text: '抱歉，AI助手暂时无法回复，请稍后再试。' };
        this.messages.push(errorMessage);
      } finally {
        this.isLoading = false;
        // 滚动到最新的消息
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },
    
    scrollToBottom() {
      const chatBody = this.$refs.chatBody;
      chatBody.scrollTop = chatBody.scrollHeight;
    },
    
    openModelManagement() {
      this.showModelManagement = true;
    },
    
    closeModelManagement() {
      this.showModelManagement = false;
      // 关闭模型管理时重新加载模型列表
      this.fetchAvailableModels();
    },
    
    handleModelUpdated() {
      // 模型更新后重新加载模型列表
      this.fetchAvailableModels();
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

.model-selector {
  margin-right: auto;
  margin-left: 1rem;
  background: #3b4b60;
  color: white;
  border: 1px solid #475569;
  border-radius: 0.5rem;
  padding: 0.25rem 0.5rem;
}

.manage-models-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #fff;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  margin-left: 0.5rem;
  transition: all 0.3s;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.manage-models-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
}

.close-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.75rem;
  cursor: pointer;
  transition: transform 0.2s;
  margin-left: 0.5rem;
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

/* 模型管理模态框样式 */
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
  z-index: 2000;
  backdrop-filter: blur(8px);
}

.model-management-container {
  background: #0f0f23;
  border-radius: 15px;
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.model-management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background: #101729;
  border-bottom: 1px solid #3c4a60;
  border-radius: 15px 15px 0 0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.model-management-header h2 {
  color: #fff;
  margin: 0;
  font-size: 24px;
}

.close-management-btn {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 32px;
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
}

.close-management-btn:hover {
  background: #1e293b;
  color: #fff;
  transform: rotate(90deg);
}

</style>