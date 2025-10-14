<!-- ModelManagement.vue -->
<template>
  <div class="model-management">
    <div class="header">
      <h2>AI模型管理</h2>
      <button class="add-model-btn" @click="showAddModelForm">添加模型</button>
    </div>

    <div class="models-list">
      <div 
        v-for="model in models" 
        :key="model.id" 
        class="model-card"
        :class="{ 'inactive': !model.is_active }"
      >
        <div class="model-info"> 
          <h3>{{ model.name }}</h3>
          <p class="provider">提供商: {{ model.provider }}</p>
          <p class="identifier">模型标识: {{ model.model_identifier }}</p>
          <p class="status">状态: {{ model.is_active ? '启用' : '禁用' }}</p>
        </div>
        
        <div class="model-actions">
          <button @click="editModel(model)" class="edit-btn">编辑</button>
          <button @click="deleteModel(model.id)" class="delete-btn">删除</button>
          <button 
            @click="toggleModelStatus(model)" 
            class="toggle-btn"
            :class="{ 'activate': !model.is_active }"
          >
            {{ model.is_active ? '禁用' : '启用' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 模型表单模态框 -->
    <div v-if="showModelForm" class="modal-overlay" @click.self="closeModelForm">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingModel ? '编辑模型' : '添加模型' }}</h3>
          <button class="close-modal" @click="closeModelForm">×</button>
        </div>
        
        <form @submit.prevent="saveModel" class="model-form">
          <div class="form-group">
            <label for="modelName">模型名称 *</label>
            <input 
              id="modelName" 
              v-model="modelForm.name" 
              type="text" 
              required
              :disabled="!!editingModel"
            />
          </div>
          
          <div class="form-group">
            <label for="modelProvider">提供商 *</label>
            <select id="modelProvider" v-model="modelForm.provider" required>
              <option value="volcengine">火山引擎 (豆包)</option>
              <option value="alibaba">阿里云 (通义千问)</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="apiKey">API密钥 *</label>
            <input 
              id="apiKey" 
              v-model="modelForm.api_key" 
              type="password" 
              required
            />
          </div>
          
          <div class="form-group">
            <label for="modelIdentifier">模型标识 *</label>
            <input 
              id="modelIdentifier" 
              v-model="modelForm.model_identifier" 
              type="text" 
              required
            />
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                v-model="modelForm.is_active" 
                type="checkbox"
              />
              启用模型
            </label>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModelForm" class="cancel-btn">取消</button>
            <button type="submit" class="save-btn">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ModelManagement',
  data() {
    return {
      models: [],
      showModelForm: false,
      editingModel: null,
      modelForm: {
        name: '',
        provider: 'volcengine',
        api_key: '',
        model_identifier: '',
        is_active: true,
        config: {}
      }
    };
  },
  async mounted() {
    await this.loadModels();
  },
  methods: {
    async loadModels() {
      try {
        const response = await axios.get('/api/models');
        this.models = response.data.models;
      } catch (error) {
        console.error('加载模型列表失败:', error);
        alert('加载模型列表失败');
      }
    },
    
    showAddModelForm() {
      this.editingModel = null;
      this.modelForm = {
        name: '',
        provider: 'volcengine',
        api_key: '',
        model_identifier: '',
        is_active: true,
        config: {}
      };
      this.showModelForm = true;
    },
    
    editModel(model) {
      this.editingModel = model;
      this.modelForm = {
        name: model.name,
        provider: model.provider,
        api_key: model.api_key,
        model_identifier: model.model_identifier,
        is_active: model.is_active,
        config: model.config ? JSON.parse(model.config) : {}
      };
      this.showModelForm = true;
    },
    
    closeModelForm() {
      this.showModelForm = false;
      this.editingModel = null;
    },
    
    async saveModel() {
      try {
        if (this.editingModel) {
          // 更新模型
          await axios.put(`/api/models/${this.editingModel.id}`, this.modelForm);
          alert('模型更新成功');
        } else {
          // 创建新模型
          await axios.post('/api/models', this.modelForm);
          alert('模型创建成功');
        }
        
        this.closeModelForm();
        await this.loadModels();
        // 通知父组件模型已更新
        this.$emit('model-updated');
      } catch (error) {
        console.error('保存模型失败:', error);
        alert(`保存模型失败: ${error.response?.data?.error || error.message}`);
      }
    },
    
    async deleteModel(modelId) {
      if (!confirm('确定要删除这个模型吗？')) {
        return;
      }
      
      try {
        await axios.delete(`/api/models/${modelId}`);
        alert('模型删除成功');
        await this.loadModels();
        // 通知父组件模型已更新
        this.$emit('model-updated');
      } catch (error) {
        console.error('删除模型失败:', error);
        alert(`删除模型失败: ${error.response?.data?.error || error.message}`);
      }
    },
    
    async toggleModelStatus(model) {
      try {
        await axios.put(`/api/models/${model.id}`, {
          is_active: !model.is_active
        });
        alert(`模型已${!model.is_active ? '启用' : '禁用'}`);
        await this.loadModels();
        // 通知父组件模型已更新
        this.$emit('model-updated');
      } catch (error) {
        console.error('更新模型状态失败:', error);
        alert(`更新模型状态失败: ${error.response?.data?.error || error.message}`);
      }
    }
  }
};
</script>

<style scoped>
.model-management {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h2 {
  color: #fff;
  font-size: 24px;
}

.add-model-btn {
  background: #5d92ff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

.add-model-btn:hover {
  background: #4779ff;
}

.models-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.model-card {
  background: #1e293b;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  border: 1px solid #3c4a60;
  transition: transform 0.2s, border-color 0.2s;
}

.model-card:hover {
  transform: translateY(-2px);
  border-color: #5d92ff;
}

.model-card.inactive {
  opacity: 0.7;
}

.model-info h3 {
  color: #fff;
  margin: 0 0 10px 0;
  font-size: 18px;
}

.model-info p {
  color: #94a3b8;
  margin: 5px 0;
  font-size: 14px;
}

.provider {
  color: #5d92ff;
}

.identifier {
  color: #94a3b8;
}

.status {
  color: #10b981;
  font-weight: 500;
}

.model-card.inactive .status {
  color: #ef4444;
}

.model-actions {
  display: flex;
  gap: 10px;
  margin-top: auto;
  padding-top: 15px;
}

.model-actions button {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.edit-btn {
  background: #3b4b60;
  color: white;
}

.edit-btn:hover {
  background: #4b5b70;
}

.delete-btn {
  background: #ef4444;
  color: white;
}

.delete-btn:hover {
  background: #dc2626;
}

.toggle-btn {
  background: #10b981;
  color: white;
}

.toggle-btn:hover {
  background: #059669;
}

.toggle-btn.activate {
  background: #f59e0b;
}

.toggle-btn.activate:hover {
  background: #d97706;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed !important;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000; /* 保证在最上层显示 */
  backdrop-filter: blur(4px);
}

.modal {
  background: #1e293b;
  border-radius: 12px;
  width: 90%;
  max-width: 520px;
  max-height: 85vh;
  overflow-y: auto;
  border: 1px solid #3c4a60;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6);
  padding-bottom: 10px;
  transform: translateY(0);
  transition: transform 0.2s ease, opacity 0.2s ease;
}

/* 打开时有轻微动画 */
.modal-overlay .modal {
  transform: translateY(0);
  opacity: 1;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #3c4a60;
  background: #101729;
  position: sticky;
  top: 0;
  z-index: 10;
}

.modal-header h3 {
  color: #fff;
  margin: 0;
}

.close-modal {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 26px;
  cursor: pointer;
  transition: color 0.2s, transform 0.2s;
}

.close-modal:hover {
  color: #fff;
  transform: rotate(90deg);
}

.model-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  color: #fff;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #3c4a60;
  background: #101729;
  color: #fff;
  font-size: 16px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #5d92ff;
}

.checkbox-label {
  display: flex;
  align-items: center;
  color: #fff;
  font-weight: normal;
  cursor: pointer;
}

.checkbox-label input {
  width: auto;
  margin-right: 10px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.form-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}

.cancel-btn {
  background: #3b4b60;
  color: white;
}

.cancel-btn:hover {
  background: #4b5b70;
}

.save-btn {
  background: #5d92ff;
  color: white;
}

.save-btn:hover {
  background: #4779ff;
}
</style>