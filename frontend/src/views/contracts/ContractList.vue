<template>
  <div class="contract-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>合同列表</span>
          <el-button type="primary" @click="handleAdd">新增合同</el-button>
        </div>
      </template>
      <el-form inline :model="searchForm">
        <el-form-item label="合作商">
          <el-select v-model="searchForm.partner_id" placeholder="请选择" clearable filterable>
            <el-option v-for="p in partners" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.contract_type" placeholder="请选择" clearable>
            <el-option v-for="t in types" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="contract_no" label="合同编号" width="120" />
        <el-table-column prop="partner_name" label="合作商" />
        <el-table-column prop="contract_type" label="类型" />
        <el-table-column prop="amount" label="金额">
          <template #default="{ row }">{{ row.amount ? row.amount.toLocaleString() : '-' }}</template>
        </el-table-column>
        <el-table-column prop="sign_date" label="签约日期" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === '执行中' ? 'success' : row.status === '已完成' ? 'info' : 'warning'">{{ row.status }}</el-tag>
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="合同编号" prop="contract_no">
          <el-input v-model="form.contract_no" />
        </el-form-item>
        <el-form-item label="合作商">
          <el-select v-model="form.partner_id" placeholder="请选择" clearable filterable>
            <el-option v-for="p in partners" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联项目">
          <el-select v-model="form.project_id" placeholder="请选择" clearable filterable>
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="合同类型">
          <el-select v-model="form.contract_type">
            <el-option v-for="t in types" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额">
          <el-input-number v-model="form.amount" :min="0" :step="10000" />
        </el-form-item>
        <el-form-item label="签约方">
          <el-input v-model="form.parties" />
        </el-form-item>
        <el-form-item label="签约日期">
          <el-date-picker v-model="form.sign_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="生效日期">
          <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="到期日期">
          <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" />
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
import { getContracts, createContract, updateContract, deleteContract, getPartnerOptions, getContractTypes, getContractStatuses, getProjects, getUserOptions } from '@/api/resources'

const loading = ref(false)
const tableData = ref([])
const pagination = ref({ page: 1, total: 0 })
const searchForm = reactive({ partner_id: null, contract_type: '', status: '' })
const partners = ref([])
const types = ref([])
const statuses = ref([])
const projects = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref()
const form = reactive({ id: null, contract_no: '', partner_id: null, project_id: null, contract_type: '', amount: null, parties: '', sign_date: '', start_date: '', end_date: '', status: '起草', notes: '' })
const rules = { contract_no: [{ required: true, message: '请输入合同编号', trigger: 'blur' }] }

const loadData = async () => {
  loading.value = true
  try {
    const res = await getContracts({ ...searchForm, page: pagination.value.page })
    tableData.value = res.items
    pagination.value.total = res.total
  } catch (e) { ElMessage.error(e.error || '加载失败') }
  finally { loading.value = false }
}

onMounted(async () => {
  partners.value = await getPartnerOptions()
  types.value = await getContractTypes()
  statuses.value = await getContractStatuses()
  projects.value = (await getProjects({ per_page: 100 })).items
  loadData()
})

const handleAdd = () => { dialogTitle.value = '新增合同'; Object.assign(form, { id: null, contract_no: '', partner_id: null, project_id: null, contract_type: '', amount: null, parties: '', sign_date: '', start_date: '', end_date: '', status: '起草', notes: '' }); dialogVisible.value = true }
const handleEdit = (row) => { dialogTitle.value = '编辑合同'; const { milestones, ...rest } = row; Object.assign(form, rest); dialogVisible.value = true }
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    form.id ? await updateContract(form.id, form) : await createContract(form)
    ElMessage.success(form.id ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.error || '操作失败') }
  finally { submitLoading.value = false }
}
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除合同"${row.contract_no}"吗？`, '提示', { type: 'warning' }).then(async () => { await deleteContract(row.id); ElMessage.success('删除成功'); loadData() }).catch(() => {})
}
</script>

<style scoped>.card-header{display:flex;justify-content:space-between;align-items:center}</style>