<template>
  <div class="project-detail">
    <el-page-header @back="router.back()" content="项目详情">
      <template #actions>
        <el-button type="primary" @click="handleEdit">编辑</el-button>
      </template>
    </el-page-header>
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header><span>基本信息</span></template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="项目名称">{{ data.name }}</el-descriptions-item>
            <el-descriptions-item label="阶段"><el-tag :type="getStageType(data.stage)">{{ data.stage }}</el-tag></el-descriptions-item>
            <el-descriptions-item label="合作商">{{ data.partner_name }}</el-descriptions-item>
            <el-descriptions-item label="负责人">{{ data.owner_name }}</el-descriptions-item>
            <el-descriptions-item label="预算">{{ data.budget ? data.budget.toLocaleString() : '-' }}</el-descriptions-item>
            <el-descriptions-item label="预计成交日期">{{ data.expected_close_date }}</el-descriptions-item>
            <el-descriptions-item label="项目来源">{{ data.source }}</el-descriptions-item>
            <el-descriptions-item label="客户行业">{{ data.industry }}</el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">{{ data.description }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        <el-card style="margin-top: 20px">
          <template #header><span>跟进记录</span></template>
          <el-timeline>
            <el-timeline-item v-for="f in followups" :key="f.id" :timestamp="f.created_at" placement="top">
              <el-card>
                <h4>{{ f.method }} - {{ f.creator_name }}</h4>
                <p>{{ f.content }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header><span>关联合同</span></template>
          <el-table :data="contracts" max-height="300">
            <el-table-column prop="contract_no" label="合同编号" />
            <el-table-column prop="amount" label="金额">
              <template #default="{ row }">{{ row.amount ? row.amount.toLocaleString() : '-' }}</template>
            </el-table-column>
            <el-table-column prop="status" label="状态" />
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
import { getProject } from '@/api/resources'
import { getFollowups } from '@/api/resources'

const route = useRoute()
const router = useRouter()
const id = route.params.id
const data = ref({})
const followups = ref([])
const contracts = ref([])

const getStageType = (stage) => ({ '线索': 'info', '跟进': 'primary', '方案': 'warning', '商务': 'warning', '签约': 'success', '交付': 'success', '结项': 'info' }[stage] || 'info')

onMounted(async () => {
  try {
    data.value = await getProject(id)
    followups.value = (await getFollowups({ project_id: id })).items
    contracts.value = data.value.contracts || []
  } catch (e) { ElMessage.error(e.error || '加载失败') }
})

const handleEdit = () => { router.push({ path: '/projects', query: { edit: id } }) }
</script>

<style scoped></style>