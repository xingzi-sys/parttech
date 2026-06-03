<template>
  <div class="user-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleAdd">新增用户</el-button>
        </div>
      </template>
      <el-form inline :model="searchForm">
        <el-form-item label="搜索">
          <el-input v-model="searchForm.search" placeholder="用户名/姓名/邮箱" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="请选择" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="real_name" label="姓名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="department" label="部门" />
        <el-table-column prop="position" label="职位" />
        <el-table-column prop="roles" label="角色">
          <template #default="{ row }">
            <el-tag v-for="r in row.roles" :key="r.id" size="small" style="margin-right: 5px">{{ r.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" link @click="handleResetPassword(row)">重置密码</el-button>
            <el-button type="success" link @click="handleToggleStatus(row)" v-if="!row.is_active">启用</el-button>
            <el-button type="danger" link @click="handleDelete(row)" v-if="row.username !== 'admin'">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="pagination.page" :total="pagination.total" layout="prev, pager, next" style="margin-top: 20px; justify-content: flex-end" @change="loadData" />
    </el-card>
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.real_name" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="form.department" />
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="form.position" />
        </el-form-item>
        <el-form-item label="角色" v-if="isAdmin">
          <el-select v-model="form.roles" multiple placeholder="请选择">
            <el-option v-for="r in allRoles" :key="r.id" :label="r.name" :value="r.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!form.id">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="状态" v-if="form.id && isAdmin">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, createUser, updateUser, deleteUser, getRoles } from '@/api/resources'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.hasRole('admin'))

const loading = ref(false)
const tableData = ref([])
const pagination = ref({ page: 1, total: 0 })
const searchForm = reactive({ search: '', is_active: null })
const allRoles = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref()
const form = reactive({ id: null, username: '', email: '', real_name: '', department: '', position: '', roles: [], password: '', is_active: true })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '请输入正确的邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur', min: 6 }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getUsers({ ...searchForm, page: pagination.value.page })
    tableData.value = res.items
    pagination.value.total = res.total
  } catch (e) { ElMessage.error(e.error || '加载失败') }
  finally { loading.value = false }
}

onMounted(async () => {
  allRoles.value = await getRoles()
  loadData()
})

const handleAdd = () => { dialogTitle.value = '新增用户'; Object.assign(form, { id: null, username: '', email: '', real_name: '', department: '', position: '', roles: [], password: '', is_active: true }); dialogVisible.value = true }
const handleEdit = (row) => { dialogTitle.value = '编辑用户'; Object.assign(form, { ...row, roles: row.roles.map(r => r.code) }); dialogVisible.value = true }
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    form.id ? await updateUser(form.id, form) : await createUser(form)
    ElMessage.success(form.id ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.error || '操作失败') }
  finally { submitLoading.value = false }
}
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除用户"${row.username}"吗？此操作不可恢复！`, '提示', { type: 'warning' }).then(async () => { await deleteUser(row.id); ElMessage.success('删除成功'); loadData() }).catch(() => {})
}
const handleToggleStatus = (row) => {
  ElMessageBox.confirm(`确定要启用用户"${row.username}"吗？`, '提示', { type: 'warning' }).then(async () => { await updateUser(row.id, { is_active: true }); ElMessage.success('启用成功'); loadData() }).catch(() => {})
}
const handleResetPassword = (row) => {
  ElMessageBox.prompt('请输入新密码', '重置密码', { confirmButtonText: '确定', cancelButtonText: '取消', inputPattern: /.{6,}/, inputErrorMessage: '密码至少6位' }).then(async ({ value }) => { await updateUser(row.id, { password: value }); ElMessage.success('密码重置成功') }).catch(() => {})
}
</script>

<style scoped>.card-header{display:flex;justify-content:space-between;align-items:center}</style>