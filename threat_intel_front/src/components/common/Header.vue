<template>
  <header class="header">
    <div class="container" style="width: 100% !important; max-width: none !important; margin: 0 !important; padding: 0 1.5rem !important; display: flex !important; justify-content: flex-start !important; align-items: center !important;">
      <div class="left-section" style="display: flex !important; align-items: center !important;">
        <h1 class="logo" style="margin: 0 !important; text-align: left !important; font-size: 1.5rem !important; position: absolute !important; left: 1.5rem !important; font-weight: bold !important; top: 50% !important; transform: translateY(-50%) !important; background: linear-gradient(135deg, #00d4ff, #ff6b9d, #c471ed) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; background-clip: text !important; text-shadow: 0 0 20px rgba(0, 212, 255, 0.5) !important;">
          🛡️ 威胁情报仪表板 🔍
        </h1>
        <AiRobot @show-ai-dialog="isChatDialogVisible = true" />
      </div>
      <div class="right-section" style="display: flex !important; align-items: center !important; margin-left: auto !important; position: absolute !important; right: 1.5rem !important; top: 50% !important; transform: translateY(-50%) !important;">
        <!-- 导航菜单（移除权限管理选项） -->
        <nav class="nav">
          <ul style="display: flex !important; gap: 2rem !important; margin: 0 !important; padding: 0 !important; list-style: none !important; flex-wrap: wrap !important; justify-content: flex-end !important;">
            <li>
              <a
                href="#"
                class="nav-link"
                :class="{ active: active === 'threat' }"
                @click.prevent="setActiveTab('threat')"
              >威胁情报🚨</a>
            </li>
            <!-- 有权限才显示：WAF协同（需要 waf:blocked:list 权限） -->
            <li v-if="hasPerm('waf:blocked:list')">
              <a
                href="#"
                class="nav-link"
                :class="{ active: active === 'waf' }"
                @click.prevent="setActiveTab('waf')"
              >WAF协同🚀</a>
            </li>
            <!-- 有权限才显示：钓鱼邮件检测（需要 phishing:list 权限） -->
            <li v-if="hasPerm('phishing:list')">
              <a
                href="#"
                class="nav-link"
                :class="{ active: active === 'phishing' }"
                @click.prevent="setActiveTab('phishing')"
              >钓鱼邮件检测🎣</a>
            </li>
            <li>
              <a
                href="#"
                class="nav-link"
                :class="{ active: active === 'tools' }"
                @click.prevent="setActiveTab('tools')"
              >工具箱🧰</a>
            </li>
            <!-- 已移除：导航菜单中的权限管理选项 -->
          </ul>
        </nav>

        <!-- 仅显示头像 + 下拉菜单（集成用户管理+权限管理） -->
        <div class="user-menu" v-if="isLoggedIn" style="margin-left: 1.5rem !important; position: relative !important;">
          <!-- 可点击头像（带交互提示） -->
          <div 
            class="avatar"
            style="width: 40px !important; height: 40px !important; border-radius: 50% !important; overflow: hidden !important; box-shadow: 0 0 10px rgba(0, 212, 255, 0.4) !important; cursor: pointer !important; transition: all 0.3s ease !important; border: 1px solid rgba(255, 255, 255, 0.1) !important;"
            @click="isDropdownOpen = !isDropdownOpen"
          >
            <img 
              src="/UserAvatar.svg" 
              alt="用户头像"
              style="width: 100% !important; height: 100% !important; object-fit: cover !important;"
            >
          </div>

          <!-- 下拉菜单（新增权限管理选项） -->
          <div 
            class="dropdown-menu"
            v-if="isDropdownOpen"
            style="position: absolute !important; top: calc(100% + 10px) !important; right: 0 !important; width: 150px !important; background: #1a1a3a !important; border-radius: 8px !important; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; z-index: 999 !important; padding: 0.8rem 0 !important;"
          >
            <!-- 用户信息项 -->
            <div class="dropdown-item" style="padding: 0.6rem 1rem !important; color: #ccc !important; font-size: 0.9rem !important; cursor: default !important; border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;">
              <div style="font-weight: 500 !important; color: #00d4ff !important; margin-bottom: 0.2rem !important;">{{ currentUser.username }}</div>
              <div style="font-size: 0.8rem !important; color: #888 !important;">角色：{{ currentUser.role }}</div>
            </div>
            
            <!-- 有权限才显示：用户管理选项（需要 user:list 权限） -->
            <div 
              class="dropdown-item"
              v-if="hasPerm('user:list')"
              style="padding: 0.6rem 1rem !important; color: #00d4ff !important; font-size: 0.9rem !important; cursor: pointer !important; transition: background 0.2s ease !important; display: flex !important; align-items: center !important; gap: 0.5rem !important; border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;"
              @click="isUserManagementOpen = true; isDropdownOpen = false"
            >
              <i class="el-icon-user" style="font-size: 0.9rem !important;"></i>
              用户管理
            </div>
            
            <!-- 有权限才显示：权限管理选项（需要 permission:manage 权限） -->
            <div 
              class="dropdown-item"
              v-if="hasPerm('permission:manage')"
              style="padding: 0.6rem 1rem !important; color: #00d4ff !important; font-size: 0.9rem !important; cursor: pointer !important; transition: background 0.2s ease !important; display: flex !important; align-items: center !important; gap: 0.5rem !important; border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;"
              @click="isPermissionManagementOpen = true; isDropdownOpen = false"
            >
              <i class="el-icon-setting" style="font-size: 0.9rem !important;"></i>
              权限管理
            </div>
            
            <!-- 注销按钮项 -->
            <div 
              class="dropdown-item logout-item"
              style="padding: 0.6rem 1rem !important; color: #ff6b6b !important; font-size: 0.9rem !important; cursor: pointer !important; transition: background 0.2s ease !important; display: flex !important; align-items: center !important; gap: 0.5rem !important;"
              @click="handleLogout"
            >
              <i class="el-icon-logout" style="font-size: 0.9rem !important;"></i>
              注销
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI聊天对话框 -->
    <AiChatDialog v-if="isChatDialogVisible" @close-ai-dialog="isChatDialogVisible = false" />
    
    <!-- 用户管理组件（弹窗） -->
    <UserManagement 
      v-model="isUserManagementOpen"
      :current-user="currentUser"
      @user-changed="handleUserChanged"
    />

    <!-- 权限管理组件（弹窗） -->
    <PermissionManagement 
      v-model="isPermissionManagementOpen"
      :current-user="currentUser"
    />
  </header>
</template>

<script>
// 导入AI聊天组件、用户管理组件、权限管理组件和权限工具
import AiRobot from '../../aichat/AiRobot.vue';
import AiChatDialog from '../../aichat/AiChatDialog.vue';
import UserManagement from '../user/UserManagement.vue';
import PermissionManagement from '../user/PermissionManagement.vue';
import { getCurrentUser, isLoggedIn } from '../../utils/auth';
import { usePermission } from '../../utils/permission';

export default {
  name: 'Header',
  components: {
    AiRobot,
    AiChatDialog,
    UserManagement,
    PermissionManagement
  },
  props: {
    active: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      isChatDialogVisible: false,
      currentUser: null,
      isLoggedIn: false,
      isDropdownOpen: false,
      isUserManagementOpen: false,
      isPermissionManagementOpen: false // 控制权限管理弹窗显示/隐藏
    };
  },
  created() {
    this.checkLoginStatus();
    document.addEventListener('click', this.closeDropdownOnClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.closeDropdownOnClickOutside);
  },
  async mounted() {
    if (this.isLoggedIn) {
      await this.initUserPermissions();
    }
  },
  watch: {
    '$parent.isLoggedIn'(newVal) {
      this.isLoggedIn = newVal;
      this.checkLoginStatus();
      this.isDropdownOpen = false;
      if (newVal) this.initUserPermissions();
    },
    currentUser(newVal) {
      this.currentUser = newVal;
    }
  },
  methods: {
    async initUserPermissions() {
      const { initUserPermissions } = usePermission();
      await initUserPermissions();
    },
    hasPerm(permissionKey) {
      const { hasPerm } = usePermission();
      return hasPerm(permissionKey);
    },
    setActiveTab(tab) {
      this.$emit('tab-change', tab);
      this.isDropdownOpen = false;
    },
    checkLoginStatus() {
      this.isLoggedIn = isLoggedIn();
      if (this.isLoggedIn) {
        this.currentUser = getCurrentUser();
      } else {
        this.currentUser = null;
      }
    },
    handleLogout() {
      if (this.$parent?.logout) {
        this.$parent.logout();
      }
      this.isDropdownOpen = false;
      this.$router.push('/login');
    },
    closeDropdownOnClickOutside(e) {
      const userMenu = document.querySelector('.user-menu');
      if (userMenu && !userMenu.contains(e.target)) {
        this.isDropdownOpen = false;
      }
    },
    handleUserChanged() {
      console.log('用户数据已更新，可在此刷新用户信息');
      this.currentUser = getCurrentUser();
      this.initUserPermissions();
    }
  }
}
</script>

<style scoped>
/* 原有样式保持不变 */
.header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
  position: relative;
  min-height: 80px;
}
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.left-section {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
}
.right-section {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  margin-left: auto;
}
.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #fff;
  margin: 0;
  text-align: left;
}
.nav ul {
  list-style: none;
  display: flex;
  gap: 2rem;
  margin: 0;
  padding: 0;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.nav-link {
  color: #fff;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  white-space: nowrap;
}
.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}
.nav-link.active {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

/* 头像交互效果 */
.avatar:hover {
  transform: scale(1.1) !important;
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.6) !important;
}

/* 下拉菜单项hover效果 */
::v-deep(.dropdown-item:hover:not(.logout-item)) {
  background: rgba(255, 255, 255, 0.05) !important;
}
::v-deep(.logout-item:hover) {
  background: rgba(255, 107, 107, 0.15) !important;
}

/* 响应式适配 */
@media (max-width: 1200px) {
  .nav ul {
    gap: 1rem;
  }
  .user-menu {
    margin-left: 1rem !important;
  }
}

@media (max-width: 992px) {
  .nav ul {
    gap: 0.5rem;
  }
  .nav-link {
    padding: 0.5rem 0.75rem;
    font-size: 0.9rem;
  }
  .avatar {
    width: 36px !important;
    height: 36px !important;
  }
}

@media (max-width: 768px) {
  .container {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
    padding: 0.8rem 1rem;
  }
  .left-section {
    justify-content: center;
    width: 100%;
  }
  .right-section {
    justify-content: center;
    width: 100%;
    margin-left: 0;
    position: static !important;
    transform: none !important;
    flex-direction: column !important;
    gap: 1rem !important;
  }
  .logo {
    text-align: center;
    font-size: 1.3rem;
    position: static !important;
    transform: none !important;
  }
  .nav ul {
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
  }
  .user-menu {
    margin-left: 0 !important;
    margin-top: 0.5rem !important;
  }
}

@media (max-width: 480px) {
  .logo {
    font-size: 1.2rem;
  }
  .nav ul {
    gap: 0.8rem;
  }
  .nav-link {
    padding: 0.3rem 0.6rem;
    font-size: 0.85rem;
  }
  .avatar {
    width: 34px !important;
    height: 34px !important;
  }
}
</style>