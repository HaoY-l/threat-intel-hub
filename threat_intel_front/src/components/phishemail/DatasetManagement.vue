<template>
  <div class="dataset-management">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>数据集管理</span>
        </div>
      </template>
      
      <!-- 数据集信息展示 -->
      <div v-if="datasetInfo.exists" class="dataset-info">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="文件名">{{ datasetInfo.filename }}</el-descriptions-item>
          <el-descriptions-item label="文件路径">{{ datasetInfo.filepath }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatFileSize(datasetInfo.file_size) }}</el-descriptions-item>
          <el-descriptions-item label="最后修改">{{ datasetInfo.last_modified }}</el-descriptions-item>
          <el-descriptions-item label="总记录数">{{ datasetInfo.total_rows }} 条</el-descriptions-item>
          <el-descriptions-item label="垃圾邮件">{{ datasetInfo.spam_count }} 条</el-descriptions-item>
          <el-descriptions-item label="正常邮件">{{ datasetInfo.ham_count }} 条</el-descriptions-item>
          <el-descriptions-item label="数据列">{{ datasetInfo.columns.join(', ') }}</el-descriptions-item>
        </el-descriptions>
      </div>
      
      <div v-else class="no-dataset">
        <el-alert
          title="数据集文件不存在"
          type="warning"
          description="请上传数据集文件"
          show-icon>
        </el-alert>
      </div>
      
      <!-- 文件上传区域 -->
      <div class="upload-section">
        <el-divider>上传新数据集</el-divider>
        <el-upload
          class="upload-demo"
          drag
          action="/phishing/dataset/upload"
          :headers="{ 'Content-Type': 'multipart/form-data' }"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          accept=".csv"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              请上传CSV格式的数据集文件，必须包含"text"和"target"列
            </div>
          </template>
        </el-upload>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

// 数据集信息
const datasetInfo = ref({
  exists: false,
  filename: '',
  filepath: '',
  file_size: 0,
  last_modified: '',
  total_rows: 0,
  spam_count: 0,
  ham_count: 0,
  columns: []
})

// 页面加载时获取数据集信息
onMounted(() => {
  loadDatasetInfo()
})

// 加载数据集信息
const loadDatasetInfo = async () => {
  try {
    const response = await fetch('/phishing/dataset/info')
    const data = await response.json()
    datasetInfo.value = data
  } catch (error) {
    ElMessage.error('加载数据集信息失败: ' + error.message)
  }
}

// 文件上传前检查
const beforeUpload = (file) => {
  const isCSV = file.type === 'text/csv' || file.name.endsWith('.csv')
  const isLt10M = file.size / 1024 / 1024 < 10
  
  if (!isCSV) {
    ElMessage.error('只能上传CSV文件!')
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB!')
  }
  return isCSV && isLt10M
}

// 上传成功处理
const handleUploadSuccess = (response, uploadFile) => {
  ElMessage.success('数据集上传成功: ' + response.message)
  loadDatasetInfo() // 重新加载数据集信息
}

// 上传失败处理
const handleUploadError = (error) => {
  ElMessage.error('数据集上传失败: ' + error.message)
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
.dataset-management {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dataset-info {
  margin-bottom: 20px;
}

.no-dataset {
  margin-bottom: 20px;
}

.upload-section {
  margin-top: 20px;
}
</style>