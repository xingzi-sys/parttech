<template>
  <div class="followup-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>跟进记录</span>
          <el-button type="primary" @click="handleAdd">新增跟进</el-button>
        </div>
      </template>
      <el-form inline :model="searchForm">
        <el-form-item label="合作商">
          <el-select v-model="searchForm.partner_id" placeholder="请选择" clearable filterable>
            <el-option v-for="p in partners" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="方式">
          <el-select v-model="searchForm.method" placeholder="请选择" clearable>
            <el-option v-for="m in methods" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="partner_name" label="合作商" />
        <el-table-column prop="project_name" label="关联项目" />
        <el-table-column prop="method" label="方式" width="80" />
        <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="creator_name" label="跟进人" />
        <el-table-column prop="created_at" label="跟进时间" />
        <el-table-column prop="next_followup_date" label="下次跟进日期" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="pagination.page" :total="pagination.total" layout="prev, pager, next" style="margin-top: 20px; justify-content: flex-end" @change="loadData" />
    </el-card>
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="合作商" prop="partner_id">
          <el-select v-model="form.partner_id" placeholder="请选择" clearable filterable>
            <el-option v-for="p in partners" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联项目">
          <el-select v-model="form.project_id" placeholder="请选择" clearable filterable>
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="跟进方式">
          <el-select v-model="form.method">
            <el-option v-for="m in methods" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="跟进内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="下次跟进日期">
          <el-date-picker v-model="form.next_followup_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="下次跟进内容">
          <el-input v-model="form.next_followup_content" type="textarea" :rows="2" />
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
import { getFollowups, createFollowup, updateFollowup, deleteFollowup, getPartnerOptions, getProjects, getFollowupMethods } from '@/api/resources'

const loading = ref(false)
const tableData = ref([])
const pagination = ref({ page: 1, total: 0 })
const searchForm = reactive({ partner_id: null, method: '' })
const partners = ref([])
const projects = ref([])
const methods = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref()
const form = reactive({ id: null, partner_id: null, project_id: null, method: '微信', content: '', next_followup_date: '', next_followup_content: '' })
const rules = { content: [{ required: true, message: '请输入跟进内容', trigger: 'blur' }] }

const loadData = async () => {
  loading.value = true
  try {
    const res = await getFollowups({ ...searchForm, page: pagination.value.page })
    tableData.value = res.items
    pagination.value.total = res.total
  } catch (e) { ElMessage.error(e.error || '加载失败') }
  finally { loading.value = false }
}

onMounted(async () => {
  partners.value = await getPartnerOptions()
  projects.value = (await getProjects({ per_page: 100 })).items
  methods.value = await getFollowupMethods()
  loadData()
})

const handleAdd = () => { dialogTitle.value = '新增跟进'; Object.assign(form, { id: null, partner_id: null, project_id: null, method: '微信', content: '', next_followup_date: '', next_followup_content: '' }); dialogVisible.value = true }
const handleEdit = (row) => { dialogTitle.value = '编辑跟进'; Object.assign(form, { ...row, next_followup_date: row.next_followup_date || '' }); dialogVisible.value = true }
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    form.id ? await updateFollowup(form.id, form) : await createFollowup(form)
    ElMessage.success(form.id ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.error || '操作失败') }
  finally { submitLoading.value = false }
}
const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除这条跟进记录吗？', '提示', { type: 'warning' }).then(async () => { await deleteFollowup(row.id); ElMessage.success('删除成功'); loadData() }).catch(() => {})
}
</script>

<style scoped>.card-header{display:flex;justify-content:space-between;align-items:center}</style>