<template>
  <div class="model-management" aria-live="polite">
    <div class="header">
      <h2>🤖 AI 模型管理</h2>
      <button class="add-model-btn" @click="showAddModelForm">
        + 添加模型
      </button>
    </div>

    <div class="models-list">
      <div 
        v-for="model in models" 
        :key="model.id" 
        class="model-card"
        :class="{ 'inactive': !model.is_active, 'active': model.is_active }"
        role="region"
        :aria-label="`模型: ${model.name}`"
      >
        <div class="model-info"> 
          <h3>{{ model.name }}</h3>
          
          <p class="identifier">模型标识: {{ model.model_identifier }}</p>
          
          <p class="status">
            状态: 
            <span :class="{ 'text-active': model.is_active, 'text-inactive': !model.is_active }">
              {{ model.is_active ? '✅ 启用' : '❌ 禁用' }}
            </span>
          </p>
        </div>
        
        <div class="model-actions">
          <button @click="editModel(model)" class="action-btn edit-btn">编辑</button>
          <button @click="deleteModel(model.id, model.name)" class="action-btn delete-btn">删除</button>
          <button 
            @click="toggleModelStatus(model)" 
            class="action-btn toggle-btn"
            :class="{ 'activate': !model.is_active }"
          >
            {{ model.is_active ? '🟢 禁用' : '🟡 启用' }}
          </button>
        </div>
      </div>

      <p v-if="models.length === 0" class="no-models-hint">
        暂无可用模型，请点击“添加模型”按钮配置你的第一个AI模型。
      </p>
    </div>

    <Teleport to="body">
      <div 
        v-if="showModelForm" 
        class="modal-overlay-teleported" 
        @click.self="closeModelForm"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div class="modal">
          <div class="modal-header">
            <h3 id="modal-title">{{ editingModel ? '编辑模型' : '添加模型' }}</h3>
            <button class="close-modal" @click="closeModelForm" aria-label="关闭表单">×</button>
          </div>
          
          <form @submit.prevent="saveModel" class="model-form">
            
            <div class="form-group">
              <label for="modelName">模型名称 <span class="required">*</span></label>
              <input 
                id="modelName" 
                v-model="modelForm.name" 
                type="text" 
                placeholder="例如: 我的豆包模型"
                required
                :disabled="!!editingModel"
              />
              <small v-if="!!editingModel" class="hint-text">模型名称不可修改</small>
            </div>
            
            <div class="form-group">
              <label for="apiKey">API密钥 <span class="required">*</span></label>
              <input 
                id="apiKey" 
                v-model="modelForm.api_key" 
                type="password" 
                placeholder="请输入API Key"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="modelIdentifier">模型标识 <span class="required">*</span></label>
              <input 
                id="modelIdentifier" 
                v-model="modelForm.model_identifier" 
                type="text" 
                placeholder="例如: doubao-lite-4k 或 gpt-3.5-turbo"
                required
              />
              <small class="hint-text">请填写模型API名称，详见官方文档。</small>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input 
                  v-model="modelForm.is_active" 
                  type="checkbox"
                />
                **启用模型** (启用后即可在聊天界面选择)
              </label>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeModelForm" class="action-btn cancel-btn">取消</button>
              <button type="submit" class="action-btn save-btn">
                {{ editingModel ? '更新并保存' : '创建模型' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
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
        // 注意：保留 provider 字段并硬编码默认值，以确保后端 API 正常工作
        provider: 'volcengine', 
        api_key: '',
        model_identifier: '',
        is_active: true,
        config: {}
      }
    };
  },
  // 核心移除: 移除 filters，因为它不再被使用
  // filters: {
  //   formatProvider(provider) {
  //     // ... logic
  //   }
  // },
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
        alert('加载模型列表失败，请检查后端服务。');
      }
    },
    
    showAddModelForm() {
      this.editingModel = null;
      this.modelForm = {
        name: '',
        // 核心：新模型创建时，硬编码默认提供商
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
        // 核心：编辑时从数据库加载 provider，但仍不在前端显示
        provider: model.provider, 
        api_key: model.api_key || '', 
        model_identifier: model.model_identifier,
        is_active: model.is_active,
        config: model.config
      };
      this.showModelForm = true;
    },
    
    closeModelForm() {
      this.showModelForm = false;
      this.editingModel = null;
    },
    
    async saveModel() {
      if (!this.modelForm.api_key.trim() || !this.modelForm.model_identifier.trim()) {
        alert('API密钥和模型标识是必填项！');
        return;
      }

      try {
        if (this.editingModel) {
          // 更新模型
          await axios.put(`/api/models/${this.editingModel.id}`, this.modelForm);
          alert('✅ 模型更新成功！');
        } else {
          // 创建新模型
          await axios.post('/api/models', this.modelForm);
          alert('🎉 模型创建成功！');
        }
        
        this.closeModelForm();
        await this.loadModels();
        this.$emit('model-updated');
      } catch (error) {
        console.error('保存模型失败:', error);
        alert(`❌ 保存模型失败: ${error.response?.data?.error || error.message}`);
      }
    },
    
    async deleteModel(modelId, modelName) {
      if (!confirm(`确定要删除模型 ${modelName} 吗？此操作不可逆！`)) {
        return;
      }
      
      try {
        await axios.delete(`/api/models/${modelId}`);
        alert('🗑️ 模型删除成功！');
        await this.loadModels();
        this.$emit('model-updated');
      } catch (error) {
        console.error('删除模型失败:', error);
        alert(`❌ 删除模型失败: ${error.response?.data?.error || error.message}`);
      }
    },
    
    async toggleModelStatus(model) {
      const newStatus = !model.is_active;
      try {
        // 确保 provider 字段被发送，即使它没有被修改
        await axios.put(`/api/models/${model.id}`, {
          is_active: newStatus,
          provider: model.provider // 确保 provider 字段随请求发送，避免后端报错
        });
        alert(`模型 ${model.name} 已${newStatus ? '启用' : '禁用'}。`);
        await this.loadModels();
        this.$emit('model-updated');
      } catch (error) {
        console.error('更新模型状态失败:', error);
        alert(`❌ 更新模型状态失败: ${error.response?.data?.error || error.message}`);
      }
    }
  }
};
</script>

<style scoped>
/* 样式保持不变 */
/* ... (所有的样式代码保持不变) ... */

.model-management {
  padding: 30px; 
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
  color: #e2e8f0; 
  font-size: 26px;
  font-weight: 700;
}

.add-model-btn {
  background: linear-gradient(135deg, #5d92ff 0%, #3b82f6 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s;
  box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
  /* 添加硬件加速 */
  transform: translateZ(0);
}

.add-model-btn:hover {
  background: linear-gradient(135deg, #4779ff 0%, #2563eb 100%);
  transform: translateY(-1px);
}

.models-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); 
  gap: 20px;
}

.model-card {
  background: #1e293b;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  border: 1px solid #3c4a60;
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  /* 添加硬件加速 */
  transform: translateZ(0);
  backface-visibility: hidden;
}

.model-card:hover {
  transform: translateY(-4px); 
  border-color: #5d92ff;
  box-shadow: 0 8px 15px rgba(59, 130, 246, 0.1);
}

.model-card.inactive {
  opacity: 0.8;
  border-left: 5px solid #ef4444;
}

.model-card.active {
  border-left: 5px solid #10b981;
}

.model-info h3 {
  color: #fff;
  margin: 0 0 10px 0;
  font-size: 20px;
  border-bottom: 1px dashed #3c4a60;
  padding-bottom: 10px;
}

.model-info p {
  color: #94a3b8;
  margin: 7px 0;
  font-size: 14px;
}

.model-info strong {
  color: #e2e8f0;
  font-weight: 600;
}

.text-active {
  color: #10b981;
  font-weight: 600;
}

.text-inactive {
  color: #ef4444;
  font-weight: 600;
}

.no-models-hint {
  grid-column: 1 / -1;
  color: #94a3b8;
  text-align: center;
  padding: 40px;
  font-size: 16px;
  background: #1e293b;
  border-radius: 12px;
  border: 1px dashed #3c4a60;
}

.model-actions {
  display: flex;
  gap: 10px;
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid #3c4a60;
}

.action-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  /* 添加硬件加速 */
  transform: translateZ(0);
}

.edit-btn {
  background: #3b4b60;
  color: white;
}

.edit-btn:hover {
  background: #4b5b70;
  transform: translateY(-1px);
}

.delete-btn {
  background: #ef4444;
  color: white;
}

.delete-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.toggle-btn {
  background: #10b981; 
  color: white;
}

.toggle-btn:hover {
  background: #059669;
  transform: translateY(-1px);
}

.toggle-btn.activate {
  background: #f59e0b; 
}

.toggle-btn.activate:hover {
  background: #d97706;
}

/* 模态框样式 - Teleport 目标 */
.modal-overlay-teleported {
  position: fixed; 
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  /* 移除影响性能的 backdrop-filter: blur(4px) */
  background: rgba(0, 0, 0, 0.9); 
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; 
  animation: modal-fade-in 0.15s ease-out;
  /* 添加硬件加速 */
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;
}

@keyframes modal-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal {
  background: #1e293b;
  border-radius: 16px; 
  width: 90%;
  max-width: 580px; 
  max-height: 90vh; 
  overflow-y: auto;
  border: 1px solid #3c4a60;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.7);
  transform: translateY(0);
  /* 简化动画以提升性能 */
  animation: modal-slide-in 0.1s ease-out;
  /* 添加硬件加速 */
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;
}

@keyframes modal-slide-in {
  from { transform: translateY(20px) scale(0.98); opacity: 0; }
  to { transform: translateY(0) scale(1); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-bottom: 1px solid #3c4a60;
  background: #101729;
  position: sticky;
  top: 0;
  z-index: 10;
  border-radius: 16px 16px 0 0;
}

.modal-header h3 {
  color: #fff;
  margin: 0;
  font-size: 20px;
}

.close-modal {
  background: #3b4b60;
  border: none;
  color: #fff;
  font-size: 22px;
  cursor: pointer;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  transition: all 0.2s;
  /* 添加硬件加速 */
  transform: translateZ(0);
}

.close-modal:hover {
  background: #ef4444;
  transform: rotate(90deg);
}

.model-form {
  padding: 30px;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  color: #fff;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 15px;
}

.required {
  color: #ef4444;
}

.hint-text {
    font-size: 12px;
    color: #64748b;
    margin-top: 5px;
    display: block;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #3c4a60;
  background: #101729;
  color: #fff;
  font-size: 16px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #5d92ff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.form-group input:disabled {
  background: #2d3748;
  color: #94a3b8;
  cursor: not-allowed;
}

.checkbox-label {
  display: flex;
  align-items: center;
  color: #e2e8f0;
  font-weight: normal;
  cursor: pointer;
}

.checkbox-label input {
  width: auto;
  margin-right: 10px;
  transform: scale(1.2);
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
}

.form-actions button {
  padding: 12px 25px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  /* 添加硬件加速 */
  transform: translateZ(0);
}

.cancel-btn {
  background: #3b4b60;
  color: white;
}
.cancel-btn:hover {
    background: #4b5b70;
}

.save-btn {
  background: linear-gradient(135deg, #5d92ff 0%, #3b82f6 100%);
  color: white;
}
.save-btn:hover {
    background: linear-gradient(135deg, #4779ff 0%, #2563eb 100%);
}
</style>