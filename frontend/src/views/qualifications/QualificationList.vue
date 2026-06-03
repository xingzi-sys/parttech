<template>
  <div class="qualification-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>资质证照</span>
          <el-button type="primary" @click="handleAdd">新增资质</el-button>
        </div>
      </template>
      <el-form inline :model="searchForm">
        <el-form-item label="合作商">
          <el-select v-model="searchForm.partner_id" placeholder="请选择" clearable filterable>
            <el-option v-for="p in partners" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="资质名称">
          <el-select v-model="searchForm.name" placeholder="请选择" clearable>
            <el-option v-for="n in names" :key="n" :label="n" :value="n" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="有效" value="有效" />
            <el-option label="即将到期" value="即将到期" />
            <el-option label="已过期" value="已过期" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button type="warning" @click="loadExpiring">查看即将到期</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="partner_name" label="合作商" />
        <el-table-column prop="name" label="资质名称" />
        <el-table-column prop="cert_no" label="证书编号" />
        <el-table-column prop="issuer" label="发证机关" />
        <el-table-column prop="issue_date" label="发证日期" />
        <el-table-column prop="valid_until" label="到期日期">
          <template #default="{ row }">
            <span :class="{ 'expired': row.status === '已过期', 'expiring': row.status === '即将到期' }">{{ row.valid_until }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === '有效' ? 'success' : row.status === '即将到期' ? 'warning' : 'danger'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
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
          <el-select v-model="form.partner_id" placeholder="请选择" filterable>
            <el-option v-for="p in partners" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="资质名称" prop="name">
          <el-select v-model="form.name" placeholder="请选择">
            <el-option v-for="n in names" :key="n" :label="n" :value="n" />
          </el-select>
        </el-form-item>
        <el-form-item label="证书编号">
          <el-input v-model="form.cert_no" />
        </el-form-item>
        <el-form-item label="发证机关">
          <el-input v-model="form.issuer" />
        </el-form-item>
        <el-form-item label="发证日期">
          <el-date-picker v-model="form.issue_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="有效期至">
          <el-date-picker v-model="form.valid_until" type="date" value-format="YYYY-MM-DD" />
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
import { getQualifications, createQualification, updateQualification, deleteQualification, getPartnerOptions, getQualificationNames, getExpiringQualifications } from '@/api/resources'

const loading = ref(false)
const tableData = ref([])
const pagination = ref({ page: 1, total: 0 })
const searchForm = reactive({ partner_id: null, name: '', status: '' })
const partners = ref([])
const names = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref()
const form = reactive({ id: null, partner_id: null, name: '', cert_no: '', issuer: '', issue_date: '', valid_until: '', notes: '' })
const rules = { partner_id: [{ required: true, message: '请选择合作商', trigger: 'change' }], name: [{ required: true, message: '请选择资质名称', trigger: 'change' }] }

const loadData = async () => {
  loading.value = true
  try {
    const res = await getQualifications({ ...searchForm, page: pagination.value.page })
    tableData.value = res.items
    pagination.value.total = res.total
  } catch (e) { ElMessage.error(e.error || '加载失败') }
  finally { loading.value = false }
}

const loadExpiring = async () => {
  loading.value = true
  try {
    tableData.value = await getExpiringQualifications(90)
    pagination.value.total = tableData.value.length
  } catch (e) { ElMessage.error(e.error || '加载失败') }
  finally { loading.value = false }
}

onMounted(async () => {
  partners.value = await getPartnerOptions()
  names.value = await getQualificationNames()
  loadData()
})

const handleAdd = () => { dialogTitle.value = '新增资质'; Object.assign(form, { id: null, partner_id: null, name: '', cert_no: '', issuer: '', issue_date: '', valid_until: '', notes: '' }); dialogVisible.value = true }
const handleEdit = (row) => { dialogTitle.value = '编辑资质'; Object.assign(form, { ...row, issue_date: row.issue_date || '', valid_until: row.valid_until || '' }); dialogVisible.value = true }
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    form.id ? await updateQualification(form.id, form) : await createQualification(form)
    ElMessage.success(form.id ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.error || '操作失败') }
  finally { submitLoading.value = false }
}
const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除这条资质记录吗？', '提示', { type: 'warning' }).then(async () => { await deleteQualification(row.id); ElMessage.success('删除成功'); loadData() }).catch(() => {})
}
</script>

<style scoped>
.card-header{display:flex;justify-content:space-between;align-items:center}
.expired{color:#f56c6c}
.expiring{color:#e6a23c}
</style>