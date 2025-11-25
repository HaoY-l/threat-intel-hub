// src/utils/auth.js
import { ElMessage } from 'element-plus';

/**
 * 获取当前登录用户信息（从本地存储读取）
 */
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * 判断是否已登录
 */
export const isLoggedIn = () => {
  return !!getCurrentUser();
};

/**
 * 判断是否为管理员角色
 */
export const isAdmin = () => {
  const user = getCurrentUser();
  return user && user.role === 'admin';
};

/**
 * 注销登录（清除本地存储，无需路由跳转，由 App.vue 处理页面切换）
 */
export const logout = () => {
  localStorage.removeItem('user');
  ElMessage.success('已成功注销');
  // 无需路由跳转，App.vue 会监听本地存储变化或直接通过父组件方法切换页面
};

/**
 * 检查用户是否有权限（配合后端 Casbin 权限规则）
 * @param {string} requiredRole - 所需角色（如 'admin'、'user'）
 * @returns {boolean} 是否有权限
 */
export const hasRolePermission = (requiredRole) => {
  if (!isLoggedIn()) return false;
  const user = getCurrentUser();
  // 管理员拥有所有权限，普通用户仅拥有 user 权限
  return user.role === 'admin' || user.role === requiredRole;
};