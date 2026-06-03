<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon partner-icon">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ overview.total_partners }}</div>
            <div class="stat-label">活跃合作商</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon project-icon">
            <el-icon><Folder /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ overview.total_projects }}</div>
            <div class="stat-label">合作项目</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon contract-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ overview.total_contracts }}</div>
            <div class="stat-label">合同总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon amount-icon">
            <el-icon><Coin /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ formatAmount(overview.total_contract_amount) }}</div>
            <div class="stat-label">合同总金额</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>合作商分布</span>
            </div>
          </template>
          <div ref="typeChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>项目漏斗</span>
            </div>
          </template>
          <div ref="funnelChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>合同金额趋势</span>
            </div>
          </template>
          <div ref="trendChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>资质到期预警</span>
              <el-tag type="warning" v-if="alerts.expiring_count > 0">{{ alerts.expiring_count }} 个即将到期</el-tag>
            </div>
          </template>
          <el-table :data="alerts.expiring" max-height="280">
            <el-table-column prop="partner_name" label="合作商" />
            <el-table-column prop="name" label="资质" />
            <el-table-column prop="valid_until" label="到期日期" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>近期动态</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="item in activities"
              :key="item.created_at"
              :timestamp="item.created_at"
              placement="top"
            >
              <el-card>
                <h4>{{ item.title }}</h4>
                <p>{{ item.description }}</p>
                <p class="activity-meta">
                  <span v-if="item.partner_name">{{ item.partner_name }}</span>
                  <span v-if="item.creator_name"> - {{ item.creator_name }}</span>
                </p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import * as echarts from 'echarts'
import { OfficeBuilding, Folder, Document, Coin } from '@element-plus/icons-vue'
import {
  getOverview,
  getPartnerDistribution,
  getProjectFunnel,
  getContractTrend,
  getQualificationAlerts,
  getRecentActivity
} from '@/api/dashboard'

const overview = ref({})
const distribution = ref({})
const funnel = ref([])
const trend = ref([])
const alerts = ref({ expiring: [], expired: [] })
const activities = ref([])

const typeChartRef = ref()
const funnelChartRef = ref()
const trendChartRef = ref()

const formatAmount = (amount) => {
  if (!amount) return '0'
  if (amount >= 100000000) return (amount / 100000000).toFixed(1) + '亿'
  if (amount >= 10000) return (amount / 10000).toFixed(1) + '万'
  return amount.toFixed(0)
}

const initCharts = async () => {
  const [overviewData, distData, funnelData, trendData, alertData, activityData] = await Promise.all([
    getOverview(),
    getPartnerDistribution(),
    getProjectFunnel(),
    getContractTrend(6),
    getQualificationAlerts(90),
    getRecentActivity(10)
  ])

  overview.value = overviewData
  distribution.value = distData
  funnel.value = funnelData
  trend.value = trendData
  alerts.value = alertData
  activities.value = activityData

  const typeChart = echarts.init(typeChartRef.value)
  typeChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: '0%' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: distData.by_type
    }]
  })

  const funnelChart = echarts.init(funnelChartRef.value)
  funnelChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: funnelData.map(i => i.name) },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data: funnelData.map(i => i.value),
      itemStyle: { color: '#409eff' }
    }]
  })

  const trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['合同数量', '合同金额'] },
    xAxis: { type: 'category', data: trendData.map(i => i.month) },
    yAxis: [{ type: 'value', name: '数量' }, { type: 'value', name: '金额' }],
    series: [
      { name: '合同数量', type: 'line', data: trendData.map(i => i.count) },
      { name: '合同金额', type: 'line', yAxisIndex: 1, data: trendData.map(i => i.amount) }
    ]
  })
}

onMounted(() => {
  initCharts()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
  margin-right: 15px;
}

.partner-icon { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.project-icon { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.contract-icon { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.amount-icon { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-meta {
  color: #909399;
  font-size: 12px;
  margin-top: 5px;
}
</style>