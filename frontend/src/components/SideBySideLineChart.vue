<template>
  <div>
    <canvas ref="canvas" style="position: relative; height:50vh;"></canvas>
  </div>
</template>

<script>
import { Line } from 'vue-chartjs'
import 'chartjs-adapter-date-fns'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  TimeScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, LinearScale, CategoryScale, TimeScale)

export default {
  name: 'SideBySideLineChart',
  components: {
    Line
  },
  props: {
    SideBySideChartData: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      required: false,
      default: () => ({})
    }
  },
  mounted() {
    this.renderChart(this.SideBySideChartData, this.options)
  },
  methods: {
    renderChart(data, options) {
      this.chart = new ChartJS(this.$refs.canvas, {
        type: 'line',
        data,
        options
      })
    },
    getChartInstance() {
      return this.chart
    },
    resetZoom() {
      if (this.chart) {
        this.chart.resetZoom()
      }
    }
  }
}
</script>

<style scoped>
.canvas{
  height: 60rem;
}
</style>
