<template>
  <el-dialog
    title="⚙️ 角色权限管理"
    v-model="isVisible"
    width="800px"
    :append-to-body="true"
    :close-on-click-modal="false"
    :before-close="handleBeforeClose"
    :destroy-on-close="true"
  >
    <div class="permission-management-container">
      <!-- 角色选择 + 权限统计 -->
      <div class="role-header">
        <el-form-item label="选择角色" class="role-select-item">
          <el-select
            v-model="selectedRole"
            placeholder="请选择需要配置的角色"
            :disabled="isLoading"
            @change="fetchRolePermissions"
            style="width: 220px;"
          >
            <!-- 适配后端返回的角色格式（直接是字符串数组） -->
            <el-option
              v-for="role in roleList"
              :key="role"
              :label="formatRoleName(role)"
              :value="role"
            />
          </el-select>
        </el-form-item>
        <div class="permission-count" v-if="selectedRole && totalPermCount > 0">
          已选权限：<span class="count-active">{{ checkedPermIds.length }}</span> / 
          <span class="count-total">{{ totalPermCount }}</span>
        </div>
      </div>

      <!-- 权限列表（带加载/无数据提示） -->
      <div class="permission-list">
        <!-- 修复skeleton的count类型错误（用数字而非字符串） -->
        <el-skeleton v-if="isLoading" :count="8" :loading="isLoading" class="skeleton-loading" />
        <div v-else-if="!permissionTree || permissionTree.length === 0" class="no-data">
          <p>暂无权限数据，请联系管理员配置权限</p>
        </div>
        <el-tree
          v-else
          :data="permissionTree"
          :props="treeProps"
          show-checkbox
          node-key="id"
          :checked-keys="checkedPermIds"
          @check="handlePermCheck"
          :disabled="isLoading"
          :default-expand-all="true"
        >
          <template #default="{ node, data }">
            <div class="permission-node">
              <span v-if="!data.permission_key" class="module-label">
                [模块] {{ node.label }}
              </span>
              <span v-else class="perm-label">
                {{ data.permission_name }}
                <button
                  class="status-btn"
                  :class="data.is_selected ? 'status-enabled' : 'status-disabled'"
                  @click.stop="togglePermission(data)"
                  :disabled="isLoading"
                >
                  <span class="status-dot"></span>
                  {{ data.is_selected ? '已拥有' : '未拥有' }}
                </button>
              </span>
            </div>
          </template>
        </el-tree>
      </div>

      <!-- 操作区域 -->
      <div class="action-area">
        <div class="batch-actions" v-if="selectedRole && totalPermCount > 0">
          <el-button
            type="text"
            @click="handleSelectAll"
            :disabled="isLoading || checkedPermIds.length === totalPermCount"
            class="batch-btn"
          >
            全选
          </el-button>
          <el-button
            type="text"
            @click="handleDeselectAll"
            :disabled="isLoading || checkedPermIds.length === 0"
            class="batch-btn"
          >
            取消全选
          </el-button>
        </div>
        <div class="action-buttons">
          <el-button
            type="primary"
            @click="handleSavePermissions"
            :loading="isLoading"
            :disabled="!selectedRole || isLoading"
          >
            保存配置
          </el-button>
          <el-button
            @click="handleReset"
            :loading="isLoading"
            :disabled="!selectedRole || isLoading"
          >
            重置选择
          </el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script>
import { ref, reactive, watch, inject, nextTick, computed } from 'vue';
import { ElMessage } from 'element-plus';

export default {
  name: 'PermissionManagement',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    currentUser: {
      type: Object,
      required: true,
      default: () => ({})
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const request = inject('request');
    if (!request) {
      console.error('❌ 未获取到 request 工具');
      ElMessage.error('初始化失败，请刷新页面重试');
      return;
    }

    // 状态管理（适配后端返回的角色是字符串数组）
    const isVisible = ref(props.modelValue);
    const isLoading = ref(false);
    const selectedRole = ref('');
    const roleList = ref([]); // 后端返回：['admin', 'user']
    const rawPermissions = ref([]);
    const permissionTree = ref([]);
    const checkedPermIds = ref([]);

    // 树形结构配置
    const treeProps = reactive({
      label: 'module_name',
      children: 'permissions',
      disabled: 'disabled'
    });

    // 计算总权限数
    const totalPermCount = computed(() => {
      let count = 0;
      permissionTree.value.forEach(module => {
        count += module.permissions?.length || 0;
      });
      return count;
    });

    // 监听弹窗显示/隐藏
    watch(() => props.modelValue, (newVal) => {
      isVisible.value = newVal;
      nextTick(() => {
        if (newVal) {
          fetchRoles().then(() => {
            if (roleList.value.length > 0) {
              selectedRole.value = roleList.value[0]; // 默认选第一个角色
              fetchRolePermissions();
            }
          });
        } else {
          resetState();
        }
      });
    }, { immediate: false });

    watch(isVisible, (newVal) => {
      emit('update:modelValue', newVal);
    });

    /**
     * 格式化角色名称（适配后端返回的字符串角色）
     */
    const formatRoleName = (role) => {
      const roleMap = {
        'admin': '管理员',
        'user': '普通用户',
        'guest': '访客'
      };
      return roleMap[role] || role;
    };

    /**
     * 重置状态
     */
    const resetState = () => {
      selectedRole.value = '';
      rawPermissions.value = [];
      permissionTree.value = [];
      checkedPermIds.value = [];
    };

    /**
     * 加载角色列表（适配后端返回：['admin', 'user']）
     */
    const fetchRoles = async () => {
      if (roleList.value.length > 0) return;
      try {
        isLoading.value = true;
        const res = await request.get('/api/permission/roles');
        console.log('角色列表接口返回：', res);
        
        // 适配后端返回的是字符串数组（而非对象数组）
        if (res?.success && Array.isArray(res.data)) {
          roleList.value = res.data;
          console.log('角色列表解析成功：', roleList.value);
        } else {
          ElMessage.error(res?.message || '加载角色列表失败');
          roleList.value = [];
        }
      } catch (error) {
        console.error('加载角色列表报错：', error);
        ElMessage.error('网络异常，加载角色列表失败');
      } finally {
        isLoading.value = false;
      }
    };

    /**
     * 加载角色权限
     */
    const fetchRolePermissions = async () => {
      if (!selectedRole.value) return;
      try {
        isLoading.value = true;
        const url = `/api/permission/role/${selectedRole.value}/permissions`;
        const res = await request.get(url);
        console.log('权限接口返回：', res);
        
        if (res?.success && Array.isArray(res.data)) {
          rawPermissions.value = res.data;
          permissionTree.value = formatPermissionTree(rawPermissions.value);
          checkedPermIds.value = rawPermissions.value
            .filter(perm => perm.is_selected)
            .map(perm => perm.id);
        } else {
          ElMessage.error(res?.message || `加载角色「${formatRoleName(selectedRole.value)}」权限失败`);
          permissionTree.value = [];
        }
      } catch (error) {
        console.error('加载权限报错：', error);
        ElMessage.error('网络异常，加载权限失败');
        permissionTree.value = [];
      } finally {
        isLoading.value = false;
      }
    };

    /**
     * 格式化树形结构
     */
    const formatPermissionTree = (permissions) => {
      if (!permissions || !permissions.length) return [];

      const moduleMap = {};
      permissions.forEach(perm => {
        const keyPrefix = perm.permission_key?.split(':')[0] || 'other';
        const moduleNameMap = {
          'user': '用户管理',
          'threat': '威胁情报查询',
          'waf': 'WAF协同',
          'history': '操作历史',
          'news': '安全新闻',
          'phishing': '钓鱼邮件检测',
          'email': '邮箱配置',
          'ai': 'AI模型配置',
          'permission': '权限管理',
          'system': '系统配置',
          'other': '其他功能'
        };
        const moduleName = moduleNameMap[keyPrefix] || keyPrefix;

        if (!moduleMap[keyPrefix]) {
          moduleMap[keyPrefix] = {
            id: `module_${keyPrefix}`,
            module_name: moduleName,
            permission_key: '',
            permissions: []
          };
        }
        moduleMap[keyPrefix].permissions.push(perm);
      });

      return Object.values(moduleMap);
    };

    /**
     * 处理勾选事件
     */
    const handlePermCheck = (checkedKeys) => {
      const newCheckedIds = checkedKeys.filter(id => typeof id === 'number');
      checkedPermIds.value = newCheckedIds;

      permissionTree.value.forEach(module => {
        module.permissions.forEach(perm => {
          perm.is_selected = newCheckedIds.includes(perm.id);
        });
      });
    };

    /**
     * 切换单个权限状态
     */
    const togglePermission = (permission) => {
      if (isLoading.value) return;
      
      const permId = permission.id;
      const currentIndex = checkedPermIds.value.indexOf(permId);
      
      if (currentIndex > -1) {
        // 当前已选中，取消选中
        checkedPermIds.value.splice(currentIndex, 1);
        permission.is_selected = false;
      } else {
        // 当前未选中，添加选中
        checkedPermIds.value.push(permId);
        permission.is_selected = true;
      }
      
      // 同步更新树的勾选状态
      handlePermCheck(checkedPermIds.value);
    };

    /**
     * 全选
     */
    const handleSelectAll = () => {
      const allPermIds = rawPermissions.value.map(perm => perm.id);
      checkedPermIds.value = allPermIds;
      handlePermCheck(allPermIds);
    };

    /**
     * 取消全选
     */
    const handleDeselectAll = () => {
      checkedPermIds.value = [];
      handlePermCheck([]);
    };

    /**
     * 保存权限
     */
    const handleSavePermissions = async () => {
      if (!selectedRole.value) {
        ElMessage.warning('请先选择角色');
        return;
      }

      try {
        isLoading.value = true;
        const url = `/api/permission/role/${selectedRole.value}/permissions`;
        const res = await request.put(url, {
          permission_ids: checkedPermIds.value
        });

        if (res?.success) {
          ElMessage.success('权限配置保存成功！普通用户需重新登录生效');
          await fetchRolePermissions();
        } else {
          ElMessage.error(res?.message || '权限配置保存失败，请重试');
        }
      } catch (error) {
        console.error('保存权限报错：', error);
        ElMessage.error('网络异常，保存权限失败');
      } finally {
        isLoading.value = false;
      }
    };

    /**
     * 重置选择
     */
    const handleReset = async () => {
      if (!selectedRole.value) return;
      try {
        isLoading.value = true;
        await fetchRolePermissions();
        ElMessage.info('已重置为当前角色的原始权限');
      } catch (error) {
        ElMessage.error('重置失败，请重试');
      } finally {
        isLoading.value = false;
      }
    };

    /**
     * 关闭弹窗
     */
    const handleBeforeClose = () => {
      nextTick(() => {
        resetState();
        emit('update:modelValue', false);
      });
    };

    return {
      isVisible,
      isLoading,
      selectedRole,
      roleList,
      permissionTree,
      checkedPermIds,
      treeProps,
      totalPermCount,
      formatRoleName,
      fetchRoles,
      fetchRolePermissions,
      handlePermCheck,
      togglePermission,
      handleSelectAll,
      handleDeselectAll,
      handleSavePermissions,
      handleReset,
      handleBeforeClose
    };
  }
};
</script>

<style scoped>
/* 样式保持不变（与之前一致） */
.permission-management-container {
  padding: 15px 0;
}

.role-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.permission-count {
  color: #e0e0e0;
  font-size: 0.9rem;
}

.count-active {
  color: #4ade80;
  font-weight: 500;
  margin: 0 2px;
}

.count-total {
  color: #94a3b8;
  margin: 0 2px;
}

::v-deep(.el-form-item__label) {
  color: #e0e0e0 !important;
  font-weight: 500;
}

::v-deep(.el-select__wrapper) {
  background: rgba(255, 255, 255, 0.05) !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
}

::v-deep(.el-select__inner) {
  color: #fff !important;
}

::v-deep(.el-option) {
  color: #fff !important;
  background: #1a1a3a !important;
}

::v-deep(.el-option:hover) {
  background: rgba(255, 255, 255, 0.1) !important;
}

.permission-list {
  max-height: 420px;
  overflow-y: auto;
  margin-bottom: 16px;
  padding: 8px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  min-height: 200px;
  color: #e0e0e0;
}

.skeleton-loading {
  --el-skeleton-bg: rgba(255, 255, 255, 0.08);
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #94a3b8;
}

::v-deep(.el-tree) {
  color: #e0e0e0 !important;
}

::v-deep(.el-tree-node) {
  line-height: 2;
}

::v-deep(.el-tree-node__content) {
  padding: 6px 8px !important;
}

::v-deep(.el-tree-node__content:hover) {
  background: rgba(255, 255, 255, 0.08) !important;
}

::v-deep(.el-checkbox__inner) {
  background: rgba(255, 255, 255, 0.05) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
}

::v-deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: #409eff !important;
  border-color: #409eff !important;
}

.permission-node {
  width: 100%;
  display: flex;
  align-items: center;
}

.module-label {
  font-weight: 600;
  color: #94a3b8 !important;
}

.perm-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.status-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  padding: 4px 10px;
  border-radius: 6px;
  margin-left: 10px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.status-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.status-btn.status-enabled {
  color: #fff;
  background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
  box-shadow: 0 2px 8px rgba(74, 222, 128, 0.3);
}

.status-btn.status-enabled:hover:not(:disabled) {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  box-shadow: 0 4px 12px rgba(74, 222, 128, 0.4);
  transform: translateY(-1px);
}

.status-btn.status-disabled {
  color: #cbd5e1;
  background: rgba(148, 163, 184, 0.2);
  border: 1px solid rgba(148, 163, 184, 0.3);
}

.status-btn.status-disabled:hover:not(:disabled) {
  background: rgba(148, 163, 184, 0.3);
  border-color: rgba(148, 163, 184, 0.5);
  transform: translateY(-1px);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  display: inline-block;
}

.action-area {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.batch-actions {
  display: flex;
  gap: 16px;
}

.batch-btn {
  color: #94a3b8 !important;
  padding: 0 !important;
}

.batch-btn:hover {
  color: #409eff !important;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.permission-list::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.permission-list::-webkit-scrollbar-track {
  background: transparent;
}

.permission-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
}

@media (max-width: 768px) {
  .role-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .action-area {
    flex-direction: column;
    align-items: flex-end;
  }
}
</style>