<template>
  <div class="contact-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>联系人列表</span>
          <el-button type="primary" @click="handleAdd">新增联系人</el-button>
        </div>
      </template>
      <el-form inline :model="searchForm">
        <el-form-item label="合作商">
          <el-select v-model="searchForm.partner_id" placeholder="请选择" clearable filterable>
            <el-option v-for="p in partners" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="partner_name" label="所属企业" />
        <el-table-column prop="position" label="职位" />
        <el-table-column prop="role" label="角色" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="is_primary" label="主联系人">
          <template #default="{ row }">
            <el-tag v-if="row.is_primary" type="success">是</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="pagination.page" :total="pagination.total" layout="prev, pager, next" style="margin-top: 20px; justify-content: flex-end" @change="loadData" />
    </el-card>
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="所属企业" prop="partner_id">
          <el-select v-model="form.partner_id" placeholder="请选择" filterable>
            <el-option v-for="p in partners" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="form.position" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option v-for="r in roles" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="微信">
          <el-input v-model="form.wechat" />
        </el-form-item>
        <el-form-item label="主联系人">
          <el-switch v-model="form.is_primary" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getContacts, createContact, updateContact, deleteContact, getPartnerOptions } from '@/api/resources'
import { getContactRoles } from '@/api/resources'

const loading = ref(false)
const tableData = ref([])
const pagination = ref({ page: 1, total: 0 })
const searchForm = reactive({ partner_id: null })
const partners = ref([])
const roles = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref()
const form = reactive({ id: null, partner_id: null, name: '', position: '', role: '', phone: '', email: '', wechat: '', is_primary: false, notes: '' })
const rules = { partner_id: [{ required: true, message: '请选择企业', trigger: 'change' }], name: [{ required: true, message: '请输入姓名', trigger: 'blur' }] }

const loadData = async () => {
  loading.value = true
  try {
    const res = await getContacts({ ...searchForm, page: pagination.value.page })
    tableData.value = res.items
    pagination.value.total = res.total
  } catch (e) { ElMessage.error(e.error || '加载失败') }
  finally { loading.value = false }
}

onMounted(async () => {
  partners.value = (await getPartnerOptions()).map(p => ({ id: p.id, name: p.name }))
  roles.value = await getContactRoles()
  loadData()
})

const handleAdd = () => { dialogTitle.value = '新增联系人'; Object.assign(form, { id: null, partner_id: null, name: '', position: '', role: '', phone: '', email: '', wechat: '', is_primary: false, notes: '' }); dialogVisible.value = true }
const handleEdit = (row) => { dialogTitle.value = '编辑联系人'; Object.assign(form, { ...row }); dialogVisible.value = true }
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    form.id ? await updateContact(form.id, form) : await createContact(form)
    ElMessage.success(form.id ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.error || '操作失败') }
  finally { submitLoading.value = false }
}
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除联系人"${row.name}"吗？`, '提示', { type: 'warning' }).then(async () => { await deleteContact(row.id); ElMessage.success('删除成功'); loadData() }).catch(() => {})
}
</script>

<style scoped>.card-header{display:flex;justify-content:space-between;align-items:center}</style>