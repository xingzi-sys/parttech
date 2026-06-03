<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h2>PartTech</h2>
        <p>智算生态合作商管理</p>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-sub-menu index="business">
          <template #title>
            <el-icon><OfficeBuilding /></el-icon>
            <span>合作商管理</span>
          </template>
          <el-menu-item index="/partners">企业管理</el-menu-item>
          <el-menu-item index="/contacts">联系人管理</el-menu-item>
          <el-menu-item index="/products">产品管理</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/projects">
          <el-icon><Folder /></el-icon>
          <span>项目管理</span>
        </el-menu-item>
        <el-menu-item index="/contracts">
          <el-icon><Document /></el-icon>
          <span>合同管理</span>
        </el-menu-item>
        <el-menu-item index="/followups">
          <el-icon><ChatDotRound /></el-icon>
          <span>跟进记录</span>
        </el-menu-item>
        <el-menu-item index="/business-terms">
          <el-icon><Coin /></el-icon>
          <span>商务条件库</span>
        </el-menu-item>
        <el-menu-item index="/qualifications">
          <el-icon><Medal /></el-icon>
          <span>资质证照</span>
        </el-menu-item>
        <el-menu-item index="/users" v-if="authStore.hasRole('admin')">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h3>{{ pageTitle }}</h3>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>{{ authStore.user?.real_name || authStore.user?.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { DataAnalysis, OfficeBuilding, Folder, Document, ChatDotRound, Coin, Medal, User } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

const pageTitles = {
  '/dashboard': '仪表盘',
  '/partners': '企业管理',
  '/partners/:id': '企业详情',
  '/contacts': '联系人管理',
  '/products': '产品管理',
  '/projects': '项目管理',
  '/projects/:id': '项目详情',
  '/contracts': '合同管理',
  '/contracts/:id': '合同详情',
  '/followups': '跟进记录',
  '/business-terms': '商务条件库',
  '/qualifications': '资质证照',
  '/users': '用户管理'
}

const pageTitle = computed(() => {
  const path = '/' + route.path.split('/')[1]
  return pageTitles[path] || 'PartTech'
})

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
  } else if (command === 'password') {
    router.push('/password')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background: #304156;
  color: #fff;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #3a4556;
}

.logo h2 {
  margin: 0;
  color: #409eff;
  font-size: 24px;
}

.logo p {
  margin: 5px 0 0;
  font-size: 12px;
  color: #8a9bb0;
}

.sidebar-menu {
  border-right: none;
  background: #304156;
}

.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  color: #bfcbd9;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-sub-menu__title:hover {
  background: #263445;
}

.sidebar-menu .el-menu-item.is-active {
  background: #409eff;
  color: #fff;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
}

.header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
}

.user-info:hover {
  background: #f5f7fa;
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
}
</style>