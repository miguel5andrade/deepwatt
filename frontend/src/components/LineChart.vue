<template>
  <div class="chart-container-wrapper">
    <canvas ref="canvas"></canvas>
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
  TimeScale,
  Filler
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  TimeScale,
  Filler
)

export default {
  name: 'LineChart',
  components: {
    Line
  },
  props: {
    chartData: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      required: false,
      default: () => ({})
    }
  },
  data() {
    return {
      chart: null, // Holds the Chart.js instance
    }
  },
  mounted() {
    this.renderChart(this.chartData, this.options)
  },
  methods: {
    renderChart(data, options) {
      // Ensure we have fill capability and set default configs if not explicitly set
      if (data.datasets) {
        data.datasets.forEach(dataset => {
          if (dataset.fill === undefined) {
            dataset.fill = true
          }
        })
      }

      // Save the Chart.js instance in the component's data
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
  },
  watch: {
    chartData: {
      deep: true,
      handler(newData) {
        if (this.chart) {
          this.chart.data = newData;
          this.chart.update();
        }
      }
    },
    options: {
      deep: true,
      handler(newOptions) {
        if (this.chart) {
          this.chart.options = newOptions;
          this.chart.update();
        }
      }
    }
  }
}
</script>

<style scoped>
.chart-container-wrapper {
  position: relative;
  height: 100%;
  width: 100%;
}

canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>
