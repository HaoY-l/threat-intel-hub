import { createRouter, createWebHistory } from 'vue-router';
import { isLoggedIn, getCurrentUser } from '@/utils/auth';
import { ElMessage } from 'element-plus';

// 👉 1. 仅同步导入登录页（未登录时唯一加载的组件）
import Login from '@/views/Login.vue';

// 👉 2. 自动扫描所有受保护组件（无需手动列举，新增组件自动识别）
const scanProtectedComponents = () => {
  const components = {};

  // 扫描布局组件（src/layout/Layout.vue）
  components.Layout = () => import('@/layout/Layout.vue');

  // 扫描 views 目录下的受保护页面（src/views/ 下除了 Login.vue 之外的所有 .vue 文件）
  const viewModules = import.meta.glob('@/views/!(Login).vue', { eager: false });
  Object.entries(viewModules).forEach(([path, component]) => {
    // 提取组件名（如 Dashboard.vue → Dashboard）
    const name = path.match(/\/([^\/]+)\.vue$/)[1];
    components[name] = component;
  });

  // 扫描 components/user 目录下的组件（如 UserManagement.vue）
  const userComponents = import.meta.glob('@/components/user/*.vue', { eager: false });
  Object.entries(userComponents).forEach(([path, component]) => {
    const name = path.match(/\/([^\/]+)\.vue$/)[1];
    components[name] = component;
  });

  return components;
};

const protectedComponents = scanProtectedComponents();

// 👉 3. 动态生成受保护路由（自动根据组件名生成路由路径）
const generateProtectedRoutes = () => {
  return Object.entries(protectedComponents)
    .filter(([name]) => name !== 'Layout') // 排除布局组件，单独处理
    .map(([name, component]) => {
      // 组件名转路由路径（如 Dashboard → dashboard，UserManagement → user-management）
      const path = name.toLowerCase().replace(/([A-Z])/g, '-$1').replace(/^-/, '');
      // 权限约定：组件名含 Admin/Management 则为 admin 权限，否则为 user 权限
      const role = name.includes('Admin') || name.includes('Management') ? 'admin' : 'user';

      return {
        path: path,
        name: name,
        component: component,
        meta: { role: role }
      };
    });
};

// 👉 4. 最终路由配置（固定结构，无需修改）
const routes = [
  // 公开路由：仅登录页
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true }
  },

  // 受保护路由：布局 + 自动生成的子路由
  {
    path: '/',
    component: protectedComponents.Layout,
    meta: { requiresAuth: true },
    children: generateProtectedRoutes() // 动态生成子路由
  },

  // 404路由
  {
    path: '/:pathMatch(.*)*',
    redirect: (to) => isLoggedIn() ? '/dashboard' : '/login'
  }
];

// 👉 5. 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// 👉 6. 全局路由守卫（固定逻辑，无需修改）
router.beforeEach((to, from, next) => {
  // 公开路由（仅登录页）：放行
  if (to.meta.public) {
    isLoggedIn() ? next('/dashboard') : next();
    return;
  }

  // 未登录：拦截所有非公开路由
  if (!isLoggedIn()) {
    ElMessage.warning('请先登录后再访问');
    next('/login');
    return;
  }

  // 已登录：校验角色权限
  const user = getCurrentUser();
  const requiredRole = to.meta.role || 'user';
  const hasPermission = user.role === 'admin' || user.role === requiredRole;

  if (!hasPermission) {
    ElMessage.error('无权限访问该页面');
    next('/dashboard');
    return;
  }

  // 已登录+有权限：放行（此时才加载对应组件）
  next();
});

export default router;