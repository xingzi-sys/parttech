<template>
  <div class="contract-detail">
    <el-page-header @back="router.back()" content="合同详情">
      <template #actions><el-button type="primary" @click="handleEdit">编辑</el-button></template>
    </el-page-header>
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header><span>基本信息</span></template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="合同编号">{{ data.contract_no }}</el-descriptions-item>
            <el-descriptions-item label="合作商">{{ data.partner_name }}</el-descriptions-item>
            <el-descriptions-item label="合同类型">{{ data.contract_type }}</el-descriptions-item>
            <el-descriptions-item label="金额">{{ data.amount ? data.amount.toLocaleString() : '-' }}</el-descriptions-item>
            <el-descriptions-item label="签约���">{{ data.parties }}</el-descriptions-item>
            <el-descriptions-item label="状态"><el-tag :type="data.status === '执行中' ? 'success' : 'info'">{{ data.status }}</el-tag></el-descriptions-item>
            <el-descriptions-item label="签约日期">{{ data.sign_date }}</el-descriptions-item>
            <el-descriptions-item label="生效日期">{{ data.start_date }}</el-descriptions-item>
            <el-descriptions-item label="到期日期">{{ data.end_date }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ data.notes }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        <el-card style="margin-top: 20px">
          <template #header><span>付款里程碑</span></template>
          <el-table :data="data.milestones || []">
            <el-table-column prop="name" label="节点" />
            <el-table-column prop="amount" label="金额"><template #default="{ row }">{{ row.amount ? row.amount.toLocaleString() : '-' }}</template></el-table-column>
            <el-table-column prop="plan_date" label="计划日期" />
            <el-table-column prop="actual_date" label="实际日期" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }"><el-tag :type="row.status === '已付款' ? 'success' : row.status === '逾期' ? 'danger' : 'warning'">{{ row.status }}</el-tag></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getContract } from '@/api/resources'

const route = useRoute()
const router = useRouter()
const id = route.params.id
const data = ref({})

onMounted(async () => { try { data.value = await getContract(id) } catch (e) { ElMessage.error(e.error || '加载失败') } })
const handleEdit = () => { router.push({ path: '/contracts', query: { edit: id } }) }
</script>

<style scoped></style>