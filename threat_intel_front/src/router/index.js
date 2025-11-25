import { createRouter, createWebHistory } from 'vue-router';
import { isLoggedIn } from '@/utils/auth'; // 之前创建的权限工具函数
import { ElMessage } from 'element-plus';

// 导入页面组件
import Home from '@/views/Home.vue';
import Login from '@/views/Login.vue';
import ThreatQuery from '@/views/ThreatQuery.vue';
import EmailConfig from '@/views/EmailConfig.vue';
import Layout from '@/layout/Layout.vue';

const routes = [
  {
    path: '/',
    component: Layout,
    children: [
      { 
        path: '', 
        name: 'Home', 
        component: Home,
        meta: { requiresAuth: true } // 关键：首页需要登录才能访问
      },
      { 
        path: 'threat-query', 
        name: 'ThreatQuery', 
        component: ThreatQuery,
        meta: { requiresAuth: true }
      },
      { 
        path: 'email-config', 
        name: 'EmailConfig', 
        component: EmailConfig,
        meta: { requiresAuth: true, role: 'admin' }
      }
    ]
  },
  { 
    path: '/login', 
    name: 'Login', 
    component: Login,
    meta: { requiresAuth: false } // 登录页无需登录
  },
  { path: '/:pathMatch(.*)*', redirect: '/' } // 404跳转首页（会被守卫拦截到登录页）
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// 路由守卫：所有需要登录的页面，未登录则跳登录页
router.beforeEach((to, from, next) => {
  // 1. 登录页直接放行
  if (to.name === 'Login') {
    next();
    return;
  }

  // 2. 所有需要登录的页面（包括首页），校验登录状态
  if (to.meta.requiresAuth || to.path === '/') { // 首页强制校验
    if (isLoggedIn()) {
      // 已登录：放行
      next();
    } else {
      // 未登录：提示并跳登录页
      ElMessage.warning('请先登录后再访问');
      next('/login'); // 跳转到登录页
    }
    return;
  }

  // 其他页面默认放行
  next();
});

export default router;