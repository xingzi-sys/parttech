<template>
  <div class="partner-detail">
    <el-page-header @back="router.back()" content="企业详情">
      <template #actions>
        <el-button type="primary" @click="handleEdit">编辑</el-button>
      </template>
    </el-page-header>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>基本信息</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="企业名称">{{ data.name }}</el-descriptions-item>
            <el-descriptions-item label="类型">{{ data.type }}</el-descriptions-item>
            <el-descriptions-item label="等级">
              <el-tag :type="getLevelType(data.level)">{{ data.level }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="data.status === '活跃' ? 'success' : 'info'">{{ data.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="统一信用代码">{{ data.credit_code }}</el-descriptions-item>
            <el-descriptions-item label="官网">
              <a v-if="data.website" :href="data.website" target="_blank" class="link">{{ data.website }}</a>
            </el-descriptions-item>
            <el-descriptions-item label="注册地" :span="2">{{ data.registered_address }}</el-descriptions-item>
            <el-descriptions-item label="标签" :span="2">
              <el-tag v-for="tag in data.tags" :key="tag" size="small" style="margin-right: 5px">{{ tag }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">{{ data.description }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>联系人</span>
              <el-button size="small" @click="showContactDialog = true">新增</el-button>
            </div>
          </template>
          <el-table :data="contacts" v-loading="loadingContacts">
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="position" label="职位" />
            <el-table-column prop="role" label="角色" />
            <el-table-column prop="phone" label="电话" />
            <el-table-column prop="email" label="邮箱" />
            <el-table-column prop="is_primary" label="主联系人">
              <template #default="{ row }">
                <el-tag v-if="row.is_primary" type="success">是</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>产品</span>
              <el-button size="small" @click="showProductDialog = true">新增</el-button>
            </div>
          </template>
          <el-table :data="products" v-loading="loadingProducts">
            <el-table-column prop="name" label="产品名称" />
            <el-table-column prop="category" label="类别" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.status === '在售' ? 'success' : 'info'">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="scenarios" label="适配场景" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <span>项目</span>
          </template>
          <el-table :data="projects" max-height="300">
            <el-table-column prop="name" label="项目名称" />
            <el-table-column prop="stage" label="阶段" />
          </el-table>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <span>资质证照</span>
          </template>
          <el-table :data="qualifications" max-height="300">
            <el-table-column prop="name" label="资质名称" />
            <el-table-column prop="valid_until" label="到期日期" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="getQualStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showContactDialog" title="新增联系人" width="500px">
      <el-form ref="contactFormRef" :model="contactForm" :rules="contactRules" label-width="80px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="contactForm.name" />
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="contactForm.position" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="contactForm.role">
            <el-option v-for="r in contactRoles" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="contactForm.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="contactForm.email" />
        </el-form-item>
        <el-form-item label="微信">
          <el-input v-model="contactForm.wechat" />
        </el-form-item>
        <el-form-item label="主联系人">
          <el-switch v-model="contactForm.is_primary" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showContactDialog = false">取消</el-button>
        <el-button type="primary" @click="saveContact">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showProductDialog" title="新增产品" width="500px">
      <el-form ref="productFormRef" :model="productForm" :rules="productRules" label-width="80px">
        <el-form-item label="产品名称" prop="name">
          <el-input v-model="productForm.name" />
        </el-form-item>
        <el-form-item label="类别">
          <el-select v-model="productForm.category">
            <el-option v-for="c in productCategories" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="productForm.status">
            <el-option v-for="s in productStatuses" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="productForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="适配场景">
          <el-input v-model="productForm.scenarios" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProductDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProduct">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPartner, getContacts, createContact, getProducts, createProduct, getProductCategories, getProductStatuses } from '@/api/partners'
import { getProjects } from '@/api/resources'
import { getQualifications } from '@/api/resources'
import { getContactRoles } from '@/api/resources'

const route = useRoute()
const router = useRouter()
const id = route.params.id

const data = ref({})
const contacts = ref([])
const products = ref([])
const projects = ref([])
const qualifications = ref([])
const loadingContacts = ref(false)
const loadingProducts = ref(false)

const showContactDialog = ref(false)
const showProductDialog = ref(false)
const contactFormRef = ref()
const productFormRef = ref()

const contactRoles = ref([])
const productCategories = ref([])
const productStatuses = ref([])

const contactForm = reactive({ name: '', position: '', role: '', phone: '', email: '', wechat: '', is_primary: false })
const productForm = reactive({ name: '', category: '', status: '在售', description: '', scenarios: '' })

const contactRules = { name: [{ required: true, message: '请输入姓名', trigger: 'blur' }] }
const productRules = { name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }] }

const getLevelType = (level) => ({ '战略': 'danger', '核心': 'warning', '普通': 'info', '潜在': 'info' }[level] || 'info')
const getQualStatusType = (status) => ({ '有效': 'success', '即将到期': 'warning', '已过期': 'danger' }[status] || 'info')

const loadData = async () => {
  try {
    data.value = await getPartner(id)
    contacts.value = (await getContacts({ partner_id: id })).items
    products.value = (await getProducts({ partner_id: id })).items
    projects.value = (await getProjects({ partner_id: id })).items
    qualifications.value = (await getQualifications({ partner_id: id })).items
  } catch (e) {
    ElMessage.error(e.error || '加载失败')
  }
}

const saveContact = async () => {
  const valid = await contactFormRef.value.validate().catch(() => false)
  if (!valid) return
  await createContact({ ...contactForm, partner_id: Number(id) })
  ElMessage.success('添加成功')
  showContactDialog.value = false
  loadData()
}

const saveProduct = async () => {
  const valid = await productFormRef.value.validate().catch(() => false)
  if (!valid) return
  await createProduct({ ...productForm, partner_id: Number(id) })
  ElMessage.success('添加成功')
  showProductDialog.value = false
  loadData()
}

const handleEdit = () => {
  router.push({ path: '/partners', query: { edit: id } })
}

onMounted(async () => {
  contactRoles.value = await getContactRoles()
  const [cats, stats] = await Promise.all([getProductCategories(), getProductStatuses()])
  productCategories.value = cats
  productStatuses.value = stats
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
</style>