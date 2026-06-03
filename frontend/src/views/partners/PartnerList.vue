<template>
  <div class="partner-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>合作商列表</span>
          <el-button type="primary" @click="handleAdd">新增合作商</el-button>
        </div>
      </template>

      <el-form inline :model="searchForm">
        <el-form-item label="搜索">
          <el-input v-model="searchForm.search" placeholder="企业名称" clearable @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.type" placeholder="请选择" clearable>
            <el-option v-for="t in types" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="searchForm.level" placeholder="请选择" clearable>
            <el-option v-for="l in levels" :key="l" :label="l" :value="l" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="企业名称" min-width="150">
          <template #default="{ row }">
            <router-link :to="`/partners/${row.id}`" class="link">{{ row.name }}</router-link>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="level" label="等级" width="80">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === '活跃' ? 'success' : 'info'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tags" label="标签" width="200">
          <template #default="{ row }">
            <el-tag v-for="tag in row.tags" :key="tag" size="small" style="margin-right: 5px">{{ tag }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="website" label="官网" min-width="150">
          <template #default="{ row }">
            <a v-if="row.website" :href="row.website" target="_blank" class="link">{{ row.website }}</a>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 20px; justify-content: flex-end"
        @change="loadData"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" @close="handleClose">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="企业名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入企业名称" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择">
            <el-option v-for="t in types" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="等级" prop="level">
          <el-select v-model="form.level" placeholder="请选择">
            <el-option v-for="l in levels" :key="l" :label="l" :value="l" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择">
            <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="统一信用代码">
          <el-input v-model="form.credit_code" placeholder="请输入统一社会信用代码" />
        </el-form-item>
        <el-form-item label="注册地">
          <el-input v-model="form.registered_address" placeholder="请输入注册地" />
        </el-form-item>
        <el-form-item label="官网">
          <el-input v-model="form.website" placeholder="请输入官网地址" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.tagsStr" placeholder="多个标签用逗号分隔" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
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
import { getPartners, createPartner, updatePartner, deletePartner, getPartnerTypes, getPartnerLevels, getPartnerStatuses } from '@/api/partners'

const loading = ref(false)
const tableData = ref([])
const pagination = ref({ page: 1, per_page: 20, total: 0 })
const searchForm = reactive({ search: '', type: '', level: '', status: '' })

const types = ref([])
const levels = ref([])
const statuses = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitLoading = ref(false)
const formRef = ref()
const form = reactive({
  id: null,
  name: '',
  type: '',
  level: '普通',
  status: '活跃',
  credit_code: '',
  registered_address: '',
  website: '',
  tagsStr: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入企业名称', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getPartners({ ...searchForm, page: pagination.value.page, per_page: pagination.value.per_page })
    tableData.value = res.items
    pagination.value = { ...pagination.value, total: res.total }
  } catch (e) {
    ElMessage.error(e.error || '加载失败')
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  const [t, l, s] = await Promise.all([getPartnerTypes(), getPartnerLevels(), getPartnerStatuses()])
  types.value = t
  levels.value = l
  statuses.value = s
}

const getLevelType = (level) => {
  const map = { '战略': 'danger', '核心': 'warning', '普通': 'info', '潜在': 'info' }
  return map[level] || 'info'
}

const handleAdd = () => {
  dialogTitle.value = '新增合作商'
  Object.assign(form, { id: null, name: '', type: '', level: '普通', status: '活跃', credit_code: '', registered_address: '', website: '', tagsStr: '', description: '' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑合作商'
  Object.assign(form, {
    id: row.id,
    name: row.name,
    type: row.type,
    level: row.level,
    status: row.status,
    credit_code: row.credit_code,
    registered_address: row.registered_address,
    website: row.website,
    tagsStr: row.tags?.join(','),
    description: row.description
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const data = { ...form, tags: form.tagsStr }
    if (form.id) {
      await updatePartner(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await createPartner(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error(e.error || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除合作商"${row.name}"吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await deletePartner(row.id)
      ElMessage.success('删除成功')
      loadData()
    })
    .catch(() => {})
}

const handleReset = () => {
  Object.assign(searchForm, { search: '', type: '', level: '', status: '' })
  pagination.value.page = 1
  loadData()
}

const handleClose = () => {
  formRef.value?.resetFields()
}

onMounted(() => {
  loadOptions()
  loadData()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.link {
  color: #409eff;
  text-decoration: none;
}
.link:hover {
  text-decoration: underline;
}
</style>