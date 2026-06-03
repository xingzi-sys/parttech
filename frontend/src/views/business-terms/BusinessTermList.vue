<template>
  <div class="business-term-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商务条件库</span>
          <el-button type="primary" @click="handleAdd">新增商务条件</el-button>
        </div>
      </template>
      <el-form inline :model="searchForm">
        <el-form-item label="合作商">
          <el-select v-model="searchForm.partner_id" placeholder="请选择" clearable filterable>
            <el-option v-for="p in partners" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="条件类型">
          <el-select v-model="searchForm.term_type" placeholder="请选择" clearable>
            <el-option v-for="t in termTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="partner_name" label="合作商" />
        <el-table-column prop="product_name" label="关联产品" />
        <el-table-column prop="term_type" label="条件类型" />
        <el-table-column prop="description" label="条件描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="valid_from" label="生效日期" />
        <el-table-column prop="valid_until" label="失效日期" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }"><el-tag :type="row.status === '生效中' ? 'success' : row.status === '已过期' ? 'danger' : 'info'">{{ row.status }}</el-tag></template>
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
          <el-select v-model="form.partner_id" placeholder="请选择" filterable @change="onPartnerChange">
            <el-option v-for="p in partners" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联产品">
          <el-select v-model="form.product_id" placeholder="请选择" clearable filterable>
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="条件类型" prop="term_type">
          <el-select v-model="form.term_type">
            <el-option v-for="t in termTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="条件描述">
          <el-input v-model="form.description" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="生效日期">
          <el-date-picker v-model="form.valid_from" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="失效日期">
          <el-date-picker v-model="form.valid_until" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option v-for="s in termStatuses" :key="s" :label="s" :value="s" />
          </el-select>
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
import { getBusinessTerms, createBusinessTerm, updateBusinessTerm, deleteBusinessTerm, getPartnerOptions, getProducts, getTermTypes, getTermStatuses } from '@/api/resources'

const loading = ref(false)
const tableData = ref([])
const pagination = ref({ page: 1, total: 0 })
const searchForm = reactive({ partner_id: null, term_type: '' })
const partners = ref([])
const products = ref([])
const termTypes = ref([])
const termStatuses = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref()
const form = reactive({ id: null, partner_id: null, product_id: null, term_type: '', description: '', valid_from: '', valid_until: '', status: '生效中' })
const rules = { partner_id: [{ required: true, message: '请选择合作商', trigger: 'change' }], term_type: [{ required: true, message: '请选择条件类型', trigger: 'change' }] }

const loadData = async () => {
  loading.value = true
  try {
    const res = await getBusinessTerms({ ...searchForm, page: pagination.value.page })
    tableData.value = res.items
    pagination.value.total = res.total
  } catch (e) { ElMessage.error(e.error || '加载失败') }
  finally { loading.value = false }
}

onMounted(async () => {
  partners.value = await getPartnerOptions()
  termTypes.value = await getTermTypes()
  termStatuses.value = await getTermStatuses()
  loadData()
})

const onPartnerChange = async (partnerId) => {
  form.product_id = null
  if (partnerId) {
    products.value = (await getProducts({ partner_id: partnerId, per_page: 100 })).items
  } else {
    products.value = []
  }
}

const handleAdd = () => { dialogTitle.value = '新增商务条件'; Object.assign(form, { id: null, partner_id: null, product_id: null, term_type: '', description: '', valid_from: '', valid_until: '', status: '生效中' }); products.value = []; dialogVisible.value = true }
const handleEdit = async (row) => { dialogTitle.value = '编辑商务条件'; Object.assign(form, { ...row, valid_from: row.valid_from || '', valid_until: row.valid_until || '' }); if (form.partner_id) products.value = (await getProducts({ partner_id: form.partner_id, per_page: 100 })).items; dialogVisible.value = true }
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    form.id ? await updateBusinessTerm(form.id, form) : await createBusinessTerm(form)
    ElMessage.success(form.id ? '更新成功' : '创建成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { ElMessage.error(e.error || '操作失败') }
  finally { submitLoading.value = false }
}
const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除这条商务条件吗？', '提示', { type: 'warning' }).then(async () => { await deleteBusinessTerm(row.id); ElMessage.success('删除成功'); loadData() }).catch(() => {})
}
</script>

<style scoped>.card-header{display:flex;justify-content:space-between;align-items:center}</style>