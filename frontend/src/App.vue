<template>
  <div id="app" class="dark-theme">
    <HeaderComponent />
    
    <!-- Default content shown on all paths except realtime -->
    <div v-if="!$route.path.startsWith('/realtime')">
      <div class="main-page">
        <TimePeriodSelector @selectedDate="onDateChange" />
        
        <div class="action-buttons">
          <router-link :to="'/realtime/' + macaddress" class="realtime-button">
            <i class="fas fa-bolt"></i> Real-time Monitoring
          </router-link>
        </div>
      </div>

      <div class="container">
        <button @click="resetZoom" class="reset-zoom-button">
          <i class="fas fa-search-minus"></i> Reset Zoom
        </button>
        
        <!-- Loading spinner -->
        <div class="loading-overlay" v-if="isLoading">
          <div class="spinner"></div>
          <div class="loading-text">Loading data...</div>
        </div>
        
        <!-- Current chart -->
        <div class="chart-container" v-if="CurrentData.labels.length > 0">
          <div class="chart-wrapper">
            <h2>Current</h2>
            <line-chart
              ref="currentChart"
              :chartData="CurrentData"
              :options="CurrentOptionsComputed"
            ></line-chart>
          </div>
        </div>
        
        <!-- Power chart -->
        <div class="chart-container" v-if="PowerData.labels.length > 0">
          <div class="chart-wrapper">
            <h2>Power</h2>
            <line-chart
              ref="powerChart"
              :chartData="PowerData"
              :options="PowerOptionsComputed"
            ></line-chart>
          </div>
        </div>

        <!-- Energy chart -->
        <div class="chart-container" v-if="EnergyData.labels.length > 0">
          <div class="chart-wrapper">
            <h2>Energy</h2>
            <line-chart
              ref="energyChart"
              :chartData="EnergyData"
              :options="EnergyOptionsComputed"
            ></line-chart>
          </div>
        </div>

        <div v-if="PowerData.labels.length === 0 && !isLoading" class="NoDataMessage">No data available</div>
      </div>
    </div>
    
    <!-- Router view for real-time page -->
    <router-view v-if="$route.path.startsWith('/realtime')" @macaddress="onMacAddressChange" />
  </div>
</template>

<script>
import axios from 'axios'
import LineChart from './components/LineChart.vue'
import TimePeriodSelector from './components/TimePeriodSelector.vue'
import HeaderComponent from './components/Header.vue'
import { RouterView } from 'vue-router'
import { Chart } from 'chart.js'
import zoomPlugin from 'chartjs-plugin-zoom'

// Register the zoom plugin
Chart.register(zoomPlugin)

export default {
  name: 'App',
  components: {
    LineChart,
    TimePeriodSelector,
    HeaderComponent,
    RouterView
  },
  data() {
    return {
      isLoading: false,
      macaddress: '',
      power_max: -1000000,
      power_min: 10000000,
      energy_max: -100000000,
      energy_min: 100000000,
      current_max: -1000000,
      current_min: 10000000,
      
      // Add Current data structure
      CurrentData: {
        labels: [],
        datasets: [
          {
            label: 'Current',
            data: [],
            borderColor: '#4bc0c0',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderWidth: 2,
            fill: true
          }
        ]
      },
      // Add Current options
      CurrentOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'time',
            time: {
              unit: 'hour',
              tooltipFormat: 'HH:mm',
              displayFormats: {
                hour: 'HH:mm'
              }
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#aaa',
              autoSkip: true,
              maxTicksLimit: 20
            },
            title: {
              display: true,
              text: 'Time',
              color: '#ddd'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Current (A)',
              color: '#ddd'
            },
            position: 'left',
            min: 0,
            max: 0,
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#aaa'
            }
          }
        },
        plugins: {
          zoom: {
            zoom: {
              wheel: {
                enabled: false,
              },
              drag: {
                enabled: true,
                backgroundColor: 'rgba(100,100,100,0.3)',
                borderColor: 'rgba(200,200,200,0.4)',
                borderWidth: 1,
              },
              mode: 'x',
            },
            pan: {
              enabled: false,
              mode: 'x',
            },
          },
          legend: {
            display: true,
            labels: {
              color: '#ddd'
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(50, 50, 50, 0.9)',
            titleColor: '#fff',
            bodyColor: '#fff',
            callbacks: {
              title: function(context) {
                const date = new Date(context[0].parsed.x);
                return date.toLocaleString('en-GB', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false
                }).replace(/\//g, '-');
              }
            }
          }
        },
        elements: {
          line: {
            tension: 0.4
          },
          point: {
            radius: 0,
            hitRadius: 1,
            hoverRadius: 6
          }
        },
        interaction: {
          mode: 'index',
          intersect: false
        },
        stacked: false
      },
      
      PowerData: {
        labels: [],
        datasets: [
          {
            label: 'Power',
            data: [],
            borderColor: '#ff7846',
            backgroundColor: 'rgba(255, 120, 70, 0.2)',
            borderWidth: 2,
            fill: true
          }
        ]
      },
      PowerOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'time',
            time: {
              unit: 'hour',
              tooltipFormat: 'HH:mm',
              displayFormats: {
                hour: 'HH:mm'
              }
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#aaa',
              autoSkip: true,
              maxTicksLimit: 20
            },
            title: {
              display: true,
              text: 'Time',
              color: '#ddd'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Power (W)',
              color: '#ddd'
            },
            position: 'left',
            min: 0,
            max: 0,
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#aaa'
            }
          }
        },
        plugins: {
          zoom: {
            zoom: {
              wheel: {
                enabled: false,
              },
              drag: {
                enabled: true,
                backgroundColor: 'rgba(100,100,100,0.3)',
                borderColor: 'rgba(200,200,200,0.4)',
                borderWidth: 1,
              },
              mode: 'x',
            },
            pan: {
              enabled: false,
              mode: 'x',
            },
          },
          legend: {
            display: true,
            labels: {
              color: '#ddd'
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(50, 50, 50, 0.9)',
            titleColor: '#fff',
            bodyColor: '#fff',
            callbacks: {
              title: function(context) {
                const date = new Date(context[0].parsed.x);
                return date.toLocaleString('en-GB', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false
                }).replace(/\//g, '-');
              }
            }
          }
        },
        elements: {
          line: {
            tension: 0.4
          },
          point: {
            radius: 0,
            hitRadius: 1,
            hoverRadius: 6
          }
        },
        interaction: {
          mode: 'index',
          intersect: false
        },
        stacked: false
      },
      EnergyData: {
        labels: [],
        datasets: [
          {
            label: 'Energy',
            data: [],
            borderColor: '#36a2eb',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderWidth: 2,
            fill: true
          }
        ]
      },
      EnergyOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'time',
            time: {
              unit: 'hour',
              tooltipFormat: 'HH:mm',
              displayFormats: {
                hour: 'HH:mm'
              }
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#aaa',
              autoSkip: true,
              maxTicksLimit: 20
            },
            title: {
              display: true,
              text: 'Time',
              color: '#ddd'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Energy (kW.h)',
              color: '#ddd'
            },
            position: 'left',
            min: 0,
            max: 0,
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#aaa'
            }
          }
        },
        plugins: {
          zoom: {
            zoom: {
              wheel: {
                enabled: false,
              },
              drag: {
                enabled: true,
                backgroundColor: 'rgba(100,100,100,0.3)',
                borderColor: 'rgba(200,200,200,0.4)',
                borderWidth: 1,
              },
              mode: 'x',
            },
            pan: {
              enabled: false,
              mode: 'x',
            },
          },
          legend: {
            display: true,
            labels: {
              color: '#ddd'
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(50, 50, 50, 0.9)',
            titleColor: '#fff',
            bodyColor: '#fff',
            callbacks: {
              title: function(context) {
                const date = new Date(context[0].parsed.x);
                return date.toLocaleString('en-GB', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false
                }).replace(/\//g, '-');
              }
            }
          }
        },
        elements: {
          line: {
            tension: 0.4
          },
          point: {
            radius: 0,
            hitRadius: 1,
            hoverRadius: 6
          }
        },
        interaction: {
          mode: 'index',
          intersect: false
        },
        stacked: false
      }
    }
  },
  computed: {
    // Add Current options computed property
    CurrentOptionsComputed() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'time',
            time: {
              unit: this.CurrentOptions.scales.x.time.unit,
              tooltipFormat: this.CurrentOptions.scales.x.time.tooltipFormat,
              displayFormats: {
                hour: 'HH:mm',
                day: 'DD'
              }
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#aaa',
              autoSkip: true,
              maxTicksLimit: this.CurrentOptions.scales.x.ticks.maxTicksLimit
            },
            title: {
              display: true,
              text: 'Time',
              color: '#ddd'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Current (A)',
              color: '#ddd'
            },
            position: 'left',
            min: this.current_min - 1,
            max: this.current_max + 1,
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#aaa'
            }
          }
        },
        plugins: {
          zoom: {
            zoom: {
              wheel: {
                enabled: false,
              },
              drag: {
                enabled: true,
                backgroundColor: 'rgba(100,100,100,0.3)',
                borderColor: 'rgba(200,200,200,0.4)',
                borderWidth: 1,
              },
              mode: 'x',
            },
            pan: {
              enabled: false,
            },
            limits: {
              x: {minRange: 60000}, // Minimum 1 minute range
            }
          },
          legend: {
            display: true,
            labels: {
              color: '#ddd'
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(50, 50, 50, 0.9)',
            titleColor: '#fff',
            bodyColor: '#fff',
            callbacks: {
              title: function(context) {
                if (!context || !context[0] || !context[0].parsed || context[0].parsed.x === undefined) {
                  return '';
                }
                
                const date = new Date(context[0].parsed.x);
                return date.toLocaleString('en-GB', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false
                }).replace(/\//g, '-');
              }
            }
          }
        },
        elements: {
          line: {
            tension: 0.4
          },
          point: {
            radius: 0,
            hitRadius: 1,
            hoverRadius: 6
          }
        },
        interaction: {
          mode: 'index',
          intersect: false
        },
        stacked: false,
        animation: {
          duration: 0
        },
        transitions: {
          zoom: {
            animation: {
              duration: 500
            }
          }
        }
      };
    },
    PowerOptionsComputed() {
      // Create a fresh copy of the options to avoid reactivity issues
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'time',
            time: {
              unit: this.PowerOptions.scales.x.time.unit,
              tooltipFormat: this.PowerOptions.scales.x.time.tooltipFormat,
              displayFormats: {
                hour: 'HH:mm',
                day: 'DD'
              }
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#aaa',
              autoSkip: true,
              maxTicksLimit: this.PowerOptions.scales.x.ticks.maxTicksLimit
            },
            title: {
              display: true,
              text: 'Time',
              color: '#ddd'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Power (W)',
              color: '#ddd'
            },
            position: 'left',
            min: this.power_min - 100,
            max: this.power_max + 100,
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#aaa'
            }
          }
        },
        plugins: {
          zoom: {
            zoom: {
              wheel: {
                enabled: false,
              },
              drag: {
                enabled: true,
                backgroundColor: 'rgba(100,100,100,0.3)',
                borderColor: 'rgba(200,200,200,0.4)',
                borderWidth: 1,
              },
              mode: 'x',
            },
            pan: {
              enabled: false,
            },
            limits: {
              x: {minRange: 60000}, // Minimum 1 minute range
            }
          },
          legend: {
            display: true,
            labels: {
              color: '#ddd'
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(50, 50, 50, 0.9)',
            titleColor: '#fff',
            bodyColor: '#fff',
            callbacks: {
              title: function(context) {
                if (!context || !context[0] || !context[0].parsed || context[0].parsed.x === undefined) {
                  return '';
                }
                
                const date = new Date(context[0].parsed.x);
                return date.toLocaleString('en-GB', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false
                }).replace(/\//g, '-');
              }
            }
          }
        },
        elements: {
          line: {
            tension: 0.4
          },
          point: {
            radius: 0,
            hitRadius: 1,
            hoverRadius: 6
          }
        },
        interaction: {
          mode: 'index',
          intersect: false
        },
        stacked: false,
        // Disable animations for performance with large datasets
        animation: {
          duration: 0
        },
        transitions: {
          zoom: {
            animation: {
              duration: 500
            }
          }
        }
      };
    },
    
    EnergyOptionsComputed() {
      // Create a fresh copy of the energy options
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'time',
            time: {
              unit: this.EnergyOptions.scales.x.time.unit,
              tooltipFormat: this.EnergyOptions.scales.x.time.tooltipFormat,
              displayFormats: {
                hour: 'HH:mm',
                day: 'DD'
              }
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#aaa',
              autoSkip: true,
              maxTicksLimit: this.EnergyOptions.scales.x.ticks.maxTicksLimit
            },
            title: {
              display: true,
              text: 'Time',
              color: '#ddd'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Energy (kW.h)',
              color: '#ddd'
            },
            position: 'left',
            min: this.energy_min - 1,
            max: this.energy_max + 1,
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            },
            ticks: {
              color: '#aaa'
            }
          }
        },
        plugins: {
          zoom: {
            zoom: {
              wheel: {
                enabled: false,
              },
              drag: {
                enabled: true,
                backgroundColor: 'rgba(100,100,100,0.3)',
                borderColor: 'rgba(200,200,200,0.4)',
                borderWidth: 1,
              },
              mode: 'x',
            },
            pan: {
              enabled: false,
            },
            limits: {
              x: {minRange: 60000}, // Minimum 1 minute range
            }
          },
          legend: {
            display: true,
            labels: {
              color: '#ddd'
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(50, 50, 50, 0.9)',
            titleColor: '#fff',
            bodyColor: '#fff',
            callbacks: {
              title: function(context) {
                if (!context || !context[0] || !context[0].parsed || context[0].parsed.x === undefined) {
                  return '';
                }
                
                const date = new Date(context[0].parsed.x);
                return date.toLocaleString('en-GB', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: false
                }).replace(/\//g, '-');
              }
            }
          }
        },
        elements: {
          line: {
            tension: 0.4
          },
          point: {
            radius: 0,
            hitRadius: 1,
            hoverRadius: 6
          }
        },
        interaction: {
          mode: 'index',
          intersect: false
        },
        stacked: false,
        // Disable animations for performance with large datasets
        animation: {
          duration: 0
        },
        transitions: {
          zoom: {
            animation: {
              duration: 500
            }
          }
        }
      };
    }
  },
  watch: {
    // Add watchers for current min/max
    current_max(newVal) {
      this.CurrentOptions.scales.y.max = newVal + 1
    },
    current_min(newVal) {
      this.CurrentOptions.scales.y.min = newVal - 1
    },
    power_max(newVal) {
      this.PowerOptions.scales.y.max = newVal + 100
    },
    power_min(newVal) {
      this.PowerOptions.scales.y.min = newVal - 100
    },
    energy_max(newVal) {
      this.EnergyOptions.scales.y.max = newVal + 1
    },
    energy_min(newVal) {
      this.EnergyOptions.scales.y.min = newVal - 1
    },
    // Watch for route changes to update macaddress
    '$route'(to, from) {
      if (to.params.macaddress && to.params.macaddress !== this.macaddress) {
        this.macaddress = to.params.macaddress;
        console.log("Route changed, new macaddress:", this.macaddress);
        if (!to.path.startsWith('/realtime')) {
          this.loadInitialData();
        }
      }
    }
  },
  methods: {
    getTimeUnit(startDate, endDate) {
      const diffInHours = (endDate - startDate) / (1000 * 60 * 60)
      if (diffInHours > 24) {
        return 'day'
      }
      return 'hour'
    },
    updateChartTimeUnit(chartOptions, timeUnit) {
      chartOptions.scales.x.time.unit = timeUnit
      chartOptions.scales.x.time.tooltipFormat = timeUnit === 'day' ? 'd - hh:mm' : 'hh:mm'
      chartOptions.scales.x.ticks.maxTicksLimit = timeUnit === 'day' ? 10 : 20
    },
    async onMacAddressChange(macaddress) {
      this.macaddress = macaddress
      const currentEpochTime = Math.floor(Date.now() / 1000)
      const selectedDate = [currentEpochTime - 86400, currentEpochTime]
      await this.fetchDataAndLoadCharts(selectedDate)
    },
    // Add data decimation function to handle large datasets
    decimateData(timestamps, values, maxDataPoints = 500) {
      // Reduce maximum points for better performance
      if (timestamps.length <= maxDataPoints) {
        return { timestamps, values };
      }
      
      // Calculate the step size needed to reduce data to max points
      const step = Math.ceil(timestamps.length / maxDataPoints);
      
      // Create decimated arrays
      const decimatedTimestamps = [];
      const decimatedValues = [];
      
      for (let i = 0; i < timestamps.length; i += step) {
        decimatedTimestamps.push(timestamps[i]);
        decimatedValues.push(values[i]);
      }
      
      return { timestamps: decimatedTimestamps, values: decimatedValues };
    },
    
    async fetchDataAndLoadCharts(selectedDate) {
      // Show loading spinner
      this.isLoading = true;
      
      try {
        // Reset min/max values before fetching
        this.power_max = -1000000;
        this.power_min = 10000000;
        this.energy_max = -100000000;
        this.energy_min = 100000000;
        this.current_max = -1000000;
        this.current_min = 10000000;
        
        // Reset data arrays with new objects (not reactive)
        this.CurrentData = {
          labels: [],
          datasets: [{
            label: 'Current',
            data: [],
            borderColor: '#4bc0c0',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderWidth: 2,
            fill: true
          }]
        };
        
        this.PowerData = {
          labels: [],
          datasets: [{
            label: 'Power',
            data: [],
            borderColor: '#ff7846',
            backgroundColor: 'rgba(255, 120, 70, 0.2)',
            borderWidth: 2,
            fill: true
          }]
        };
        
        this.EnergyData = {
          labels: [],
          datasets: [{
            label: 'Energy',
            data: [],
            borderColor: '#36a2eb',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderWidth: 2,
            fill: true
          }]
        };
	const encodedId= encodeURIComponent(this.macaddress);
        const url = `http://51.44.178.184:5501/data/${encodedId}?startTime=${selectedDate[0]}&endTime=${selectedDate[1]}` ;
        let response;

        try {
          response = await fetch(url);
          if (!response.ok) {
            console.log(`Response status: ${response.status}`);
          }
        } catch (error) {
          console.error(error.message);
        }
        const json = await response.json();
        
        
          
        
        // Process data first, storing in local variables
        const tempTimes = [];
        const tempCurrentValues = []; // New array for current values
        const tempPowerValues = [];
        const tempEnergyValues = [];
        
        /*
        let previousTime = 0;
        let previousEnergy = 0;
        let count = 0;*/

        if (Array.isArray(json) && json.length > 0) {
          json.forEach((element) => {

            try {
              const time = new Date(element.timestamp * 1000);
              const current = parseFloat(element.rms_current) || 0;
              const power = parseFloat(element.power) || 0;
              const energy = parseFloat(element.dailyEnergy) || 0 ;
              
              // Calculate time difference and energy
              /*
              let timeDiff;
              let energy;
              if(count != 0){
                timeDiff = element.timestamp - previousTime;
                energy = ((power / 1000) * timeDiff / 3600) + previousEnergy;
              }else{
                //first point
                energy = 0;
              }
              
              
              previousTime = element.timestamp;
              previousEnergy = energy;*/
              
              // Update max/min values for chart scaling
              if (power > this.power_max) this.power_max = power;
              if (power < this.power_min) this.power_min = power;
              if (energy > this.energy_max) this.energy_max = energy;
              if (energy < this.energy_min) this.energy_min = energy;
              if (current > this.current_max) this.current_max = current;
              if (current < this.current_min) this.current_min = current;
              
              // Store in temporary arrays
              tempTimes.push(time);
              tempCurrentValues.push(current); // Store current values
              tempPowerValues.push(power);
              tempEnergyValues.push(energy);
              // count++;
            } catch (err) {
              console.error("Error processing data point:", err);
            }
          });
        }
        
        // Set minimum values if they're still at initial state
        if (this.power_min > this.power_max) {
          this.power_min = 0;
          this.power_max = 100;
        }
        
        if (this.energy_min > this.energy_max) {
          this.energy_min = 0;
          this.energy_max = 1;
        }
        
        if (this.current_min > this.current_max) {
          this.current_min = 0;
          this.current_max = 5;
        }
        
        // Decimate data if there are too many points
        const maxPoints = 500; // Reduced from 1000 to 500 for better performance
        const decimatedCurrent = this.decimateData(tempTimes, tempCurrentValues, maxPoints);
        const decimatedPower = this.decimateData(tempTimes, tempPowerValues, maxPoints);
        const decimatedEnergy = this.decimateData(tempTimes, tempEnergyValues, maxPoints);
        
        // Create completely new objects for the chart data to avoid reactivity issues
        this.CurrentData = {
          labels: [...decimatedCurrent.timestamps],
          datasets: [{
            label: 'Current',
            data: [...decimatedCurrent.values],
            borderColor: '#4bc0c0',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderWidth: 2,
            fill: true
          }]
        };
        
        this.PowerData = {
          labels: [...decimatedPower.timestamps],
          datasets: [{
            label: 'Power',
            data: [...decimatedPower.values],
            borderColor: '#ff7846',
            backgroundColor: 'rgba(255, 120, 70, 0.2)',
            borderWidth: 2,
            fill: true
          }]
        };
        
        this.EnergyData = {
          labels: [...decimatedEnergy.timestamps],
          datasets: [{
            label: 'Energy',
            data: [...decimatedEnergy.values],
            borderColor: '#36a2eb',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderWidth: 2,
            fill: true
          }]
        };
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        // Hide loading spinner when done, regardless of success or error
        this.isLoading = false;
      }
    },
    
    async onDateChange(newDate) {
      const timeUnit = this.getTimeUnit(newDate[0] * 1000, newDate[1] * 1000);

      // Update chart time units
      this.PowerOptions = {
        ...this.PowerOptions,
        scales: {
          ...this.PowerOptions.scales,
          x: {
            ...this.PowerOptions.scales.x,
            time: {
              ...this.PowerOptions.scales.x.time,
              unit: timeUnit,
              tooltipFormat: timeUnit === 'day' ? 'd - hh:mm' : 'hh:mm'
            },
            ticks: {
              ...this.PowerOptions.scales.x.ticks,
              maxTicksLimit: timeUnit === 'day' ? 10 : 20
            }
          }
        }
      };
      
      this.EnergyOptions = {
        ...this.EnergyOptions,
        scales: {
          ...this.EnergyOptions.scales,
          x: {
            ...this.EnergyOptions.scales.x,
            time: {
              ...this.EnergyOptions.scales.x.time,
              unit: timeUnit,
              tooltipFormat: timeUnit === 'day' ? 'd - hh:mm' : 'hh:mm'
            },
            ticks: {
              ...this.EnergyOptions.scales.x.ticks,
              maxTicksLimit: timeUnit === 'day' ? 10 : 20
            }
          }
        }
      };

      await this.fetchDataAndLoadCharts(newDate);
    },
    
    resetZoom() {
      try {
        const currentChartInstance = this.$refs.currentChart?.getChartInstance();
        const powerChartInstance = this.$refs.powerChart?.getChartInstance();
        const energyChartInstance = this.$refs.energyChart?.getChartInstance();
        
        if (currentChartInstance && currentChartInstance.resetZoom) currentChartInstance.resetZoom();
        if (powerChartInstance && powerChartInstance.resetZoom) powerChartInstance.resetZoom();
        if (energyChartInstance && energyChartInstance.resetZoom) energyChartInstance.resetZoom();
      } catch (err) {
        console.error("Error resetting zoom:", err);
      }
    },
    loadInitialData() {
      const currentEpochTime = Math.floor(Date.now() / 1000);
      const selectedDate = [currentEpochTime - 86400, currentEpochTime];
      this.fetchDataAndLoadCharts(selectedDate);
    }
  },
  created() {
    // Check for macaddress in URL on initial load
    if (this.$route.params && this.$route.params.macaddress) {
      this.macaddress = this.$route.params.macaddress;
      console.log("Found macaddress in URL:", this.macaddress);
      this.loadInitialData();
    }
  }
}
</script>

<style>
/* Global dark theme styles */
.dark-theme {
  background-color: #1a1a2e;
  color: #f1f1f1;
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.NoDataMessage {
  margin-top: 20px;
  text-align: center;
  align-items: center;
  font-family: 'Roboto', sans-serif;
  margin-bottom: 20px;
  color: #ccc;
  font-size: 18px;
  opacity: 0.7;
}

body {
  padding: 0;
  margin: 0;
  font-family: 'Roboto', sans-serif;
  background-color: #1a1a2e;
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
}

.container {
  padding: 15px;
  max-width: 1200px;
  margin: 0 auto;
}

.chart-container {
  margin-bottom: 30px;
}

.chart-wrapper {
  border: 1px solid #16213e;
  border-radius: 12px;
  padding: 20px;
  background-color: #0f3460;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  height: 400px;
  position: relative;
  overflow: hidden;
}

.chart-wrapper h2 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #e94560;
  text-align: center;
  font-size: 1.4rem;
  font-weight: 500;
}

.main-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  margin: 20px 0;
}

/* Reset zoom button styling */
.reset-zoom-button {
  margin-bottom: 15px;
  background-color: #e94560;
  color: #fff;
  border: none;
  padding: 10px 18px;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'Roboto', sans-serif;
  font-size: 14px;
  font-weight: 500;
  display: block;
  transition: background-color 0.3s ease;
}

.reset-zoom-button:hover {
  background-color: #d13350;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .reset-zoom-button {
    display: none; /* Hide reset zoom button on mobile */
  }
  
  .chart-wrapper {
    height: 300px;
    padding: 15px;
  }
  
  .container {
    padding: 10px;
  }
}

@media (max-width: 480px) {
  .chart-wrapper {
    height: 250px;
    padding: 10px;
  }
  
  .chart-wrapper h2 {
    font-size: 16px;
    margin-bottom: 10px;
  }
}

/* Loading spinner styles */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(10, 10, 30, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  border-top-color: #e94560;
  animation: spin 1s ease-in-out infinite;
}

.loading-text {
  color: #fff;
  margin-top: 20px;
  font-size: 18px;
  font-weight: 500;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.action-buttons {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  width: 100%;
}

.realtime-button {
  background-color: #e94560;
  color: #fff !important; /* Override any default link color */
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.realtime-button:hover {
  background-color: #d13350 !important;
  transform: translateY(-3px);
}

/* Add Font Awesome Icons */
.fa-bolt {
  margin-right: 5px;
}

@media (max-width: 480px) {
  .realtime-button {
    width: 100%;
    justify-content: center;
    padding: 10px;
    font-size: 14px;
  }
}
</style>
