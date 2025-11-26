<template>
  <el-dialog
    title="👥 用户管理"
    v-model="isVisible"
    width="600px"
    :append-to-body="true"
    :close-on-click-modal="false"
  >
    <!-- 新增用户表单（有权限才显示：需要 user:add 权限） -->
    <el-form 
      v-if="hasPerm('user:add')"
      :model="newUser" 
      :rules="userRules" 
      ref="userFormRef" 
      label-width="100px" 
      class="mb-4"
    >
      <el-form-item label="用户名" prop="username">
        <el-input v-model="newUser.username" placeholder="请输入用户名" :disabled="isLoading" class="black-text" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="newUser.password" type="password" placeholder="请输入密码（至少6位）" :disabled="isLoading" class="black-text"/>
      </el-form-item>
      <el-form-item label="角色" prop="role">
        <el-select v-model="newUser.role" placeholder="请选择角色" :disabled="isLoading">
          <el-option label="普通用户" value="user" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleAddUser" :loading="isLoading">新增用户</el-button>
        <el-button @click="resetForm" :loading="isLoading">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 分割线（有新增表单时才显示） -->
    <div v-if="hasPerm('user:add')" style="height: 1px; background: rgba(255,255,255,0.1); margin: 1rem 0;"></div>

    <!-- 用户列表 -->
    <div class="user-list-container" style="max-height: 400px; overflow-y: auto;">
      <el-table :data="userList" border :header-cell-style="tableHeaderStyle" :cell-style="tableCellStyle" :loading="isLoading">
        <el-table-column label="用户名" prop="username" align="center" />
        <el-table-column label="角色" prop="role" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'primary' : 'success'">
              {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="220">
          <template #default="scope">
            <!-- 删除按钮（有权限+不能删除自己） -->
            <el-button 
              type="text" 
              color="#ff4d4f" 
              @click="handleDeleteUser(scope.row.username)"
              :disabled="!hasPerm('user:delete') || scope.row.username === currentUser.username || isLoading"
            >
              删除
            </el-button>

            <!-- 重置密码按钮（有权限才显示：需要 user:add 权限） -->
            <el-button 
              type="text" 
              color="#409EFF" 
              @click="handleResetPassword(scope.row.username)"
              :disabled="!hasPerm('user:add') || isLoading"
            >
              重置密码
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 无用户提示 -->
    <div v-if="userList.length === 0 && !isLoading" style="text-align: center; padding: 2rem; color: #999;">
      暂无用户数据{{ hasPerm('user:add') ? '，请新增用户' : '' }}
    </div>
  </el-dialog>
</template>

<script>
import { ref, reactive, watch, inject, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import { usePermission } from '@/utils/permission'; // 新增：导入权限工具

export default {
  name: 'UserManagement',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    currentUser: {
      type: Object,
      required: true,
      default: () => ({ username: '' })
    }
  },
  emits: ['update:modelValue', 'user-changed'],
  setup(props, { emit }) {
    const request = inject('request');
    if (!request) {
      console.error('❌ 未获取到request工具');
      ElMessage.error('初始化失败，请刷新页面重试');
      return;
    }

    const isVisible = ref(props.modelValue);
    const isLoading = ref(false);
    const userFormRef = ref(null);
    const userList = ref([]);
    const { hasPerm } = usePermission(); // 新增：获取权限判断函数

    const newUser = reactive({
      username: '',
      password: '',
      role: 'user'
    });

    const userRules = reactive({
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度在3-20位之间', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少6位', trigger: 'blur' }
      ],
      role: [
        { required: true, message: '请选择角色', trigger: 'change' }
      ]
    });

    watch(() => props.modelValue, (newVal) => {
      isVisible.value = newVal;
      nextTick(() => {
        if (newVal) fetchUserList();
      });
    }, { immediate: true });

    watch(isVisible, (newVal) => emit('update:modelValue', newVal));

    const fetchUserList = async () => {
      try {
        isLoading.value = true;
        const res = await request.get('/api/auth/users');
        if (res?.success) userList.value = res.data || [];
        else ElMessage.error(res?.message || '加载用户列表失败');
      } catch {
        ElMessage.error('网络异常，无法加载用户数据');
      } finally {
        isLoading.value = false;
      }
    };

    const handleAddUser = async () => {
      const form = userFormRef.value;
      if (!form) return;
      try {
        await form.validate();
        isLoading.value = true;
        const res = await request.post('/api/auth/users', newUser);
        if (res?.success) {
          ElMessage.success('新增用户成功！');
          resetForm();
          fetchUserList();
          emit('user-changed');
        } else ElMessage.error(res?.message || '新增失败');
      } catch {
        ElMessage.error('网络异常，新增失败');
      } finally {
        isLoading.value = false;
      }
    };

    const handleDeleteUser = async (username) => {
      if (!username || username === props.currentUser.username) {
        ElMessage.warning('不能删除当前登录用户！');
        return;
      }
      if (!hasPerm('user:delete')) { // 校验删除权限
        ElMessage.error('无删除用户权限！');
        return;
      }
      if (window.confirm(`确定删除用户「${username}」吗？`)) {
        try {
          isLoading.value = true;
          const res = await request.delete(`/api/auth/users/${username}`);
          if (res?.success) {
            ElMessage.success('删除成功！');
            fetchUserList();
            emit('user-changed');
          } else ElMessage.error(res?.message || '删除失败');
        } catch {
          ElMessage.error('网络异常，删除失败');
        } finally {
          isLoading.value = false;
        }
      }
    };

    const resetForm = () => {
      newUser.username = '';
      newUser.password = '';
      newUser.role = 'user';
      if (userFormRef.value) userFormRef.value.clearValidate();
    };

    const handleResetPassword = async (username) => {
      if (!username) return;
      if (!hasPerm('user:add')) { // 校验重置密码权限（复用新增用户权限）
        ElMessage.error('无重置密码权限！');
        return;
      }
      const newPassword = window.prompt(`请输入用户「${username}」的新密码（至少6位）`);
      if (!newPassword || newPassword.length < 6) {
        ElMessage.warning('密码长度至少6位');
        return;
      }
      try {
        isLoading.value = true;
        const res = await request.put(`/api/auth/users/${username}/reset_password`, { password: newPassword });
        if (res?.success) ElMessage.success(`用户「${username}」密码已重置`);
        else ElMessage.error(res?.message || '重置密码失败');
      } catch {
        ElMessage.error('网络异常，无法重置密码');
      } finally {
        isLoading.value = false;
      }
    };

    const tableHeaderStyle = { background: 'rgba(255,255,255,0.05)', color: '#e0e0e0', fontWeight: 500 };
    const tableCellStyle = { background: 'transparent', color: '#ccc' };

    return {
      isVisible,
      isLoading,
      userFormRef,
      newUser,
      userRules,
      userList,
      currentUser: props.currentUser,
      tableHeaderStyle,
      tableCellStyle,
      handleAddUser,
      handleDeleteUser,
      resetForm,
      fetchUserList,
      handleResetPassword,
      hasPerm // 暴露权限判断函数到模板
    };
  }
};
</script>

<style scoped>
::v-deep(.el-form-item__label) { color: #e0e0e0 !important; }
::v-deep(.el-input__wrapper), ::v-deep(.el-select__wrapper) { background: rgba(255,255,255,0.05) !important; border-color: rgba(255,255,255,0.1) !important; }
::v-deep(.el-input__inner), ::v-deep(.el-select__inner) { color: #fff !important; }
::v-deep(.el-option) { color: #fff !important; background: #1a1a3a !important; }
::v-deep(.el-option:hover) { background: rgba(255,255,255,0.1) !important; }
::v-deep(.el-table) { background: transparent !important; border-color: rgba(255,255,255,0.1) !important; }
::v-deep(.el-table__row:hover > td) { background: rgba(255,255,255,0.05) !important; }
::v-deep(.el-table__border) { border-color: rgba(255,255,255,0.1) !important; }
.black-text ::v-deep(.el-input__inner) { color: #000 !important; }
</style>