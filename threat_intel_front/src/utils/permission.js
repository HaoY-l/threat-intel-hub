import { getCurrentUser, isLoggedIn } from './auth';
import { ElMessage } from 'element-plus';
import request from '@/utils/request'; // 导入项目实际的请求工具

// 缓存键名
const PERMISSION_CACHE_KEY = 'user_permissions';

/**
 * 清除权限缓存（注销登录时调用）
 */
export const clearPermissionCache = () => { // ✅ 移到函数外部定义
  localStorage.removeItem(PERMISSION_CACHE_KEY);
};

/**
 * 权限工具函数（全局复用）
 */
export function usePermission() {
  /**
   * 初始化用户权限（登录后调用，缓存到本地）
   * @returns {Promise<Array>} 权限标识列表
   */
  const initUserPermissions = async () => {
    if (!isLoggedIn()) {
      clearPermissionCache();
      return [];
    }

    // 先从缓存读取，避免重复请求
    const cachedPerms = getPermissionCache();
    if (cachedPerms.length > 0) {
      return cachedPerms;
    }

    try {
      const user = getCurrentUser();
      const res = await request.get(`/api/permission/role/${user.role}/permissions`);
      
      if (res?.success) {
        const permissions = res.data
          .filter(perm => perm.is_selected)
          .map(perm => perm.permission_key);
        
        setPermissionCache(permissions);
        return permissions;
      } else {
        ElMessage.error('权限初始化失败，部分功能可能无法使用');
        clearPermissionCache();
        return [];
      }
    } catch (error) {
      ElMessage.error(`网络异常，权限初始化失败: ${error.message || ''}`);
      clearPermissionCache();
      return [];
    }
  };

  /**
   * 校验是否拥有指定权限
   * @param {string} permissionKey - 权限标识（如 'user:list'）
   * @returns {boolean} 有权限返回 true，无则返回 false
   */
  const hasPerm = (permissionKey) => {
    if (!permissionKey) return false;
    if (!isLoggedIn()) return false;

    const permissions = getPermissionCache();
    return permissions.includes(permissionKey);
  };

  /**
   * 获取本地缓存的权限列表
   * @returns {Array} 权限标识列表
   */
  const getPermissionCache = () => {
    const cache = localStorage.getItem(PERMISSION_CACHE_KEY);
    return cache ? JSON.parse(cache) : [];
  };

  /**
   * 设置权限缓存
   * @param {Array} permissions - 权限标识列表
   */
  const setPermissionCache = (permissions) => {
    localStorage.setItem(PERMISSION_CACHE_KEY, JSON.stringify(permissions));
  };

  return {
    initUserPermissions,
    hasPerm,
    getPermissionCache,
    setPermissionCache,
    clearPermissionCache // ✅ 通过 return 暴露给函数外部
  };
}

// 全局注册（可选）
// import { usePermission } from '@/utils/permission';
// app.config.globalProperties.$hasPerm = usePermission().hasPerm;