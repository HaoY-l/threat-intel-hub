<template>
  <el-menu mode="horizontal" :default-active="activePath">
    <!-- 首页（所有角色可见） -->
    <el-menu-item index="/">
      <el-icon><House /></el-icon>
      <span>首页</span>
    </el-menu-item>

    <!-- 威胁情报查询（所有登录用户可见） -->
    <el-menu-item index="/threat-query" v-if="isLoggedIn">
      <el-icon><Search /></el-icon>
      <span>威胁情报查询</span>
    </el-menu-item>

    <!-- 邮箱配置（仅管理员可见） -->
    <el-menu-item index="/email-config" v-if="isAdmin">
      <el-icon><Setting /></el-icon>
      <span>邮箱配置</span>
    </el-menu-item>

    <!-- WAF黑名单管理（仅管理员可见） -->
    <el-menu-item index="/waf-blacklist" v-if="isAdmin">
      <el-icon><Lock /></el-icon>
      <span>WAF黑名单管理</span>
    </el-menu-item>

    <!-- 注销按钮（已登录状态可见） -->
    <el-menu-item index="logout" v-if="isLoggedIn" @click="handleLogout">
      <el-icon><ArrowLeft /></el-icon>
      <span>注销</span>
    </el-menu-item>

    <!-- 登录入口（未登录状态可见） -->
    <el-menu-item index="/login" v-else @click="goToLogin">
      <el-icon><User /></el-icon>
      <span>登录</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
// 最新 Element Plus 图标
import { 
  House, 
  Search, 
  Setting, 
  Lock, 
  ArrowLeft, 
  User 
} from '@element-plus/icons-vue';
import { isLoggedIn, isAdmin, logout } from '@/utils/auth';

// 路由
const route = useRoute();
const router = useRouter();

// 当前激活菜单
const activePath = computed(() => route.path);

// 跳转登录
const goToLogin = () => {
  router.push('/login');
};

// 注销
const handleLogout = () => {
  logout();
};
</script>
