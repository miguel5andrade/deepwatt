<template>
  <div>
    <img src="@/assets/mtb-logo.png" alt="Company Logo" class="logo" />
    <div class="chart-container">
      <LineChart :data="voltageData" :options="chartOptions" />
    </div>
    <div class="chart-container">
      <LineChart :data="currentData" :options="chartOptions" />
    </div>
    <div class="chart-container">
      <LineChart :data="temperatureData" :options="chartOptions" />
    </div>
  </div>
</template>

<script>
import LineChart from '@/components/LineChart.vue'

export default {
  name: 'Home',
  components: {
    LineChart
  },
  data() {
    return {
      voltageData: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        datasets: [
          {
            label: 'Voltage',
            data: [65, 59, 80, 81, 56, 55, 40],
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            fill: true
          }
        ]
      },
      currentData: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        datasets: [
          {
            label: 'Current',
            data: [28, 48, 40, 19, 86, 27, 90],
            borderColor: 'rgba(255, 99, 132, 1)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            fill: true
          }
        ]
      },
      temperatureData: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        datasets: [
          {
            label: 'Temperature',
            data: [35, 25, 30, 40, 45, 35, 25],
            borderColor: 'rgba(54, 162, 235, 1)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            fill: true
          }
        ]
      },
      chartOptions: {
        responsive: false,
        maintainAspectRatio: false
      }
    }
  }
}
</script>

<style scoped>
.logo {
  width: 100px;
  position: fixed;
  top: 10px;
  left: 10px;
}
.chart-container {
  margin-top: 60px;
  height: 400px;
}
</style>
