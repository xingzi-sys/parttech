<template>
  <div class="project-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>项目列表</span>
          <el-button type="primary" @click="handleAdd">新增项目</el-button>
        </div>
      </template>
      <el-form inline :model="searchForm">
        <el-form-item label="合作商">
          <el-select v-model="searchForm.partner_id" placeholder="请选择" clearable filterable>
            <el-option v-for="p in partners" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="阶段">
          <el-select v-model="searchForm.stage" placeholder="请选择" clearable>
            <el-option v-for="s in stages" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="searchForm.owner_id" placeholder="请选择" clearable>
            <el-option v-for="u in users" :key="u.id" :label="u.name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="项目名称" min-width="150">
          <template #default="{ row }">
            <router-link :to="`/projects/${row.id}`" class="link">{{ row.name }}</router-link>
          </template>
        </el-table-column>
        <el-table-column prop="partner_name" label="合作商" />
        <el-table-column prop="stage" label="阶段" width="80">
          <template #default="{ row }">
            <el-tag :type="getStageType(row.stage)">{{ row.stage }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="budget" label="预算">
          <template #default="{ row }">{{ row.budget ? row.budget.toLocaleString() : '-' }}</template>
        </el-table-column>
        <el-table-column prop="owner_name" label="负责人" />
        <el-table-column prop="expected_close_date" label="预计成交日期" />
        <el-table-column label="操作" width="150">
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
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="合作商">
          <el-select v-model="form.partner_id" placeholder="请选择" clearable filterable>
            <el-option v-for="p in partners" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="阶段">
          <el-select v-model="form.stage">
            <el-option v-for="s in stages" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="预算">
          <el-input-number v-model="form.budget" :min="0" :step="10000" />
        </el-form-item>
        <el-form-item label="预计成交日期">
          <el-date-picker v-model="form.expected_close_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="form.owner_id" placeholder="请选择">
            <el-option v-for="u in users" :key="u.id" :label="u.name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目来源">
          <el-input v-model="form.source" />
        </el-form-item>
        <el-form-item label="客户行业">
          <el-input v-model="form.industry" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
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
import { getProjects, createProject, updateProject, deleteProject, getPartnerOptions, getProjectStages, getUserOptions } from '@/api/resources'

const loading = ref(false)
const tableData = ref([])
const pagination = ref({ page: 1, total: 0 })
const searchForm = reactive({ partner_id: null, stage: '', owner_id: null })
const partners = ref([])
const stages = ref([])
const users = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref()
const form = reactive({ id: null, name: '', partner_id: null, stage: '线索', budget: null, expected_close_date: '', owner_id: null, source: '', industry: '', description: '' })
const rules = { name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }] }

const getStageType = (stage) => {
  const map = { '线索': 'info', '跟进': 'primary', '方案': 'warning', '商务': 'warning', '签约': 'success', '交付': 'success', '结项': 'info' }
  return map[stage] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getProjects({ ...searchForm, page: pagination.value.page })
    tableData.value = res.items
    pagination.value.total = res.total
  } catch (e) { ElMessage.error(e.error || '加载失败') }
  finally { loading.value = false }
}

onMounted(async () => {
  partners.value = await getPartnerOptions()
  stages.value = await getProjectStages()
  users.value = await getUserOptions()
  loadData()
})

const handleAdd = () => { dialogTitle.value = '新增项目'; Object.assign(form, { id: null, name: '', partner_id: null, stage: '线索', budget: null, expected_close_date: '', owner_id: null, source: '', industry: '', description: '' }); dialogVisible.value = true }
const handleEdit = (row) => { dialogTitle.value = '编辑项目'; Object.assign(form, { ...row, expected_close_date: row.expected_close_date || '' }); dialogVisible.value = true }
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    form.id ? await updateProject(form.id, form) : await createProject(form)
    ElMessage.success(form.id ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.error || '操作失败') }
  finally { submitLoading.value = false }
}
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除项目"${row.name}"吗？`, '提示', { type: 'warning' }).then(async () => { await deleteProject(row.id); ElMessage.success('删除成功'); loadData() }).catch(() => {})
}
</script>

<style scoped>.card-header{display:flex;justify-content:space-between;align-items:center}.link{color:#409eff;text-decoration:none}</style>