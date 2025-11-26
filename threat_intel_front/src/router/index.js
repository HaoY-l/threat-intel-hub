import { createRouter, createWebHistory } from 'vue-router';
import { isLoggedIn, getCurrentUser } from '@/utils/auth';
import { usePermission } from '@/utils/permission';  // 新增：导入权限工具
import { ElMessage } from 'element-plus';

// 👉 1. 仅同步导入登录页（未登录时唯一加载的组件）
import Login from '@/views/Login.vue';

// 👉 2. 自动扫描所有受保护组件（无需手动列举，新增组件自动识别）
const scanProtectedComponents = () => {
  const components = {};

  // 扫描布局组件（src/layout/Layout.vue）
  components.Layout = () => import('@/layout/Navbar.vue');

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

// 👉 3. 动态生成受保护路由（自动根据组件名生成路由路径，新增权限标识配置）
const generateProtectedRoutes = () => {
  return Object.entries(protectedComponents)
    .filter(([name]) => name !== 'Layout') // 排除布局组件，单独处理
    .map(([name, component]) => {
      // 组件名转路由路径（如 Dashboard.vue → dashboard，UserManagement → user-management）
      const path = name.toLowerCase().replace(/([A-Z])/g, '-$1').replace(/^-/, '');
      
      // 路由权限标识配置（根据组件功能绑定对应的 permission_key）
      let permissionKey = '';
      if (name.includes('UserManagement')) permissionKey = 'user:list'; // 用户管理页面 → 需要 user:list 权限
      else if (name.includes('Waf')) permissionKey = 'waf:blocked:list'; // WAF相关页面 → 需要 waf:blocked:list 权限
      else if (name.includes('Phishing')) permissionKey = 'phishing:list'; // 钓鱼邮件页面 → 需要 phishing:list 权限
      else permissionKey = ''; // 其他页面默认无需特殊权限（仅登录即可）

      return {
        path: path,
        name: name,
        component: component,
        meta: { 
          requiresAuth: true, // 需要登录
          permissionKey: permissionKey // 绑定权限标识（为空则仅登录即可访问）
        }
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

// 👉 6. 全局路由守卫（修改为动态权限校验）
router.beforeEach(async (to, from, next) => {
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

  // 已登录：获取用户信息和权限工具
  const user = getCurrentUser();
  const { initUserPermissions, hasPerm } = usePermission();
  
  // 初始化用户权限（首次登录时加载，缓存到本地）
  await initUserPermissions();

  // 无需特殊权限的路由：直接放行（仅登录即可）
  if (!to.meta.permissionKey) {
    next();
    return;
  }

  // 需要特殊权限的路由：校验权限
  const hasPermission = hasPerm(to.meta.permissionKey);
  if (hasPermission) {
    next(); // 有权限：放行
  } else {
    ElMessage.error(`无「${to.meta.permissionKey}」权限，禁止访问该页面`);
    next(from.path); // 无权限：回退到之前的页面
  }
});

export default router;