import { ElMessage } from 'element-plus';
import router from '@/router'; 
import { clearPermissionCache } from './permission'; // 导入清除权限缓存的方法

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
 * 登录成功：存储用户信息 + 跳转首页
 * @param {Object} userInfo - 后端返回的用户信息（含 role 字段）
 */
export const loginSuccess = (userInfo) => {
  localStorage.setItem('user', JSON.stringify(userInfo));
  ElMessage.success('登录成功');
  router.push('/'); // 跳首页
};

/**
 * 注销登录：清除本地存储 + 清除权限缓存 + 跳转登录页
 */
export const logout = () => {
  localStorage.removeItem('user');
  clearPermissionCache(); // 注销时同时清除权限缓存
  ElMessage.success('已成功注销');
  router.push('/login'); // 跳登录页
};

/**
 * 检查用户是否有权限访问指定路由
 */
export const hasRoutePermission = (route) => {
  if (!isLoggedIn()) return false;
  const user = getCurrentUser();
  const requiredRole = route.meta.role;
  return user.role === 'admin' || user.role === requiredRole;
};

/**
 * 过滤有权限的路由（用于侧边栏渲染）
 */
export const filterAuthorizedRoutes = (routes) => {
  return routes.filter(route => {
    if (route.meta?.requiresAuth === false) return false;
    if (route.meta?.role && !hasRoutePermission(route)) return false;
    if (route.children && route.children.length > 0) {
      route.children = filterAuthorizedRoutes(route.children);
      return route.children.length > 0;
    }
    return true;
  });
};