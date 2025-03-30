<template>
  <div class="realtime-container">
    <!-- Removed duplicate HeaderComponent -->
    
    <div class="content">
      <div class="connection-status" :class="{ connected: isConnected, disconnected: !isConnected }">
        {{ connectionStatus }}
      </div>
      
      <div class="realtime-header">
        <h1>Real-time Consumption</h1>
        <p class="device-id" v-if="deviceId">Device ID: {{ deviceId }}</p>
      </div>
      
      <!-- Budget settings -->
      <div class="budget-container">
        <div class="budget-input-wrapper">
          <label for="daily-budget">Daily Budget (kWh):</label>
          <input 
            type="number" 
            id="daily-budget" 
            v-model="dailyBudget" 
            min="0.1" 
            step="0.1" 
            @change="updateBudget"
            class="budget-input" 
          />
          <label for="feedback-device" class="mt-2">Feedback Device MAC:</label>
          <input 
            type="text" 
            id="feedback-device" 
            v-model="feedbackDeviceId" 
            @change="updateBudget"
            class="budget-input"
            placeholder="Optional feedback device ID" 
          />
          <div class="budget-status" v-if="budgetStatus">{{ budgetStatus }}</div>
        </div>
      </div>
      
      <!-- Budget usage visualization -->
      <div class="budget-usage-container" v-if="dailyBudget > 0">
        <div class="doughnut-chart-container">
          <canvas ref="budgetChart"></canvas>
        </div>
        <div class="budget-stats">
          <div class="usage-percentage" :class="getBudgetUsageClass">
            {{ usagePercentage }}%
          </div>
          <div class="usage-label">of daily budget</div>
          <div class="usage-values">
            {{ todayEnergy.toFixed(2) }} / {{ dailyBudget }} kWh
          </div>
        </div>
      </div>
      
      <div class="realtime-cards">
        <div class="card">
          <h2>Current</h2>
          <div class="value">{{ formatValue(current, 'A') }}</div>
        </div>
        
        <div class="card">
          <h2>Power</h2>
          <div class="value">{{ formatValue(power, 'W') }}</div>
        </div>
        
        <div class="card energy-card">
          <h2>Today's Energy</h2>
          <div class="value">{{ formatValue(todayEnergy, 'kWh') }}</div>
        </div>
        
        <div class="card money-card">
          <h2>Today's Cost</h2>
          <div class="value">{{ formatMoney(todayEnergy * 0.24) }}</div>
        </div>
      </div>
      
      <div class="back-button-container">
        <button class="back-button" @click="goBack">
          <i class="fas fa-arrow-left"></i> Back to Dashboard
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, DoughnutController, ArcElement, Tooltip } from 'chart.js';

// Register required chart components
Chart.register(DoughnutController, ArcElement, Tooltip);

export default {
  name: 'RealTimeConsumption',
  components: {
    // Removed HeaderComponent
  },
  props: {
    macaddress: String
  },
  data() {
    return {
      pollInterval: null,
      isConnected: false,
      connectionStatus: 'Connecting...',
      current: 0,
      power: 0,
      todayEnergy: 0,
      deviceId: '',
      retryCount: 0,
      maxRetries: 5,
      
      // Budget related data
      dailyBudget: 0,
      feedbackDeviceId: '',
      budgetStatus: '',
      budgetChart: null,
      usagePercentage: 0,
      
      // Chart update control
      requestCounter: 0,
      chartUpdateFrequency: 30, // Update every minute (30 requests at 2-second intervals)
      lastChartUpdateTime: 0,
      
      // Chart update queue
      pendingChartUpdate: false,
      updateTimeout: null
    }
  },
  computed: {
    getBudgetUsageClass() {
      if (this.usagePercentage >= 100) {
        return 'over-budget';
      } else if (this.usagePercentage >= 80) {
        return 'near-budget';
      } else {
        return 'under-budget';
      }
    }
  },
  async created() {
    this.deviceId = this.$route.params.macaddress || this.macaddress || '';
    console.log("RealTime component created with deviceId:", this.deviceId);
    
    try {
      // Try to fetch existing budget from API
      const url = `http://51.44.178.184:5501/budget/${this.deviceId}`;
       
      const response = await fetch(url);
      if (response.ok) {
	const json = await response.json();
        this.dailyBudget = json.budget;
        this.feedbackDeviceId = json.feedback_device_id;
        this.budgetStatus = 'Budget loaded from server';
      }
    } catch (error) {
        this.budgetStatus = 'Failed to load budget, using default budget';
      
    }
    this.startPolling();
  },

  beforeUnmount() {
    this.stopPolling();
    // Destroy chart to prevent memory leaks
    if (this.budgetChart) {
      this.budgetChart.destroy();
    }
  },
  methods: {
    startPolling() {
      // Immediately fetch data once
      this.fetchRealtimeData();
      
      // Then set up interval for polling every 2 seconds
      this.pollInterval = setInterval(() => {
        this.fetchRealtimeData();
      }, 2000);
    },
    
    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval);
        this.pollInterval = null;
      }
    },
    
    async fetchRealtimeData() {
      try {
        const url = `http://51.44.178.184:5501/realtime/${this.deviceId || 'default'}`;

        const response = await fetch(url);
        const json = await response.json();

    
        this.current = json.rms_current || 0;
        this.power = json.power || 0;
        this.todayEnergy = json.dailyEnergy || 0;
        
        // Calculate budget usage percentage
        this.calculateUsagePercentage();
        
        // Increment request counter
        this.requestCounter++;
        if(this.requestCounter === 1){
          this.initBudgetChart();
        }
        
       
        
        // Only update chart every chartUpdateFrequency requests
        const shouldUpdateChart = this.requestCounter % this.chartUpdateFrequency === 0;
        
        if (this.budgetChart && shouldUpdateChart) {
          console.log(`Updating chart on request #${this.requestCounter}`);
          // Add a timestamp to prevent rapid consecutive updates
          const now = Date.now();
          if (now - this.lastChartUpdateTime > 1000) { // Ensure at least 1 second between updates
            this.lastChartUpdateTime = now;
            this.updateBudgetChart();
          }
        } 
        
        // Update connection status
        this.isConnected = true;
        this.connectionStatus = 'Connected';
        this.retryCount = 0;
        
      } catch (error) {
        console.log("Error fetching real-time data:", error.toString(), JSON.stringify(error));
        this.isConnected = false;
        this.connectionStatus = 'Connection Error';
        
        // Implement retry logic
        this.retryCount++;
        if (this.retryCount > this.maxRetries) {
          this.connectionStatus = 'Failed to connect after multiple attempts';
          this.stopPolling();
        }
      }
    },
    
    formatValue(value, unit) {
      // Format numbers to 2 decimal places
      return `${parseFloat(value).toFixed(2)} ${unit}`;
    },
    
    formatMoney(value) {
      return `${parseFloat(value).toFixed(2)} €`;
    },
    
    goBack() {
      if (this.deviceId) {
        this.$router.push(`/${this.deviceId}`);
      } else {
        this.$router.push('/');
      }
    },
    
    // New methods for budget functionality
    calculateUsagePercentage() {
      if (this.dailyBudget > 0) {
        this.usagePercentage = Math.round((this.todayEnergy / this.dailyBudget) * 100);
      } else {
        this.usagePercentage = 0;
      }
      console.log("calculateUsagePercentage called");
    },
    
    async updateBudget() {
      try {
        // Save to API
	await fetch(`http://51.44.178.184:5501/update-budget/${this.deviceId}`, {
  method: "POST",
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    budget: this.dailyBudget,
    feedback_device_id: this.feedbackDeviceId
  }),
});     
        this.budgetStatus = 'Budget updated successfully';
        
        // Update chart
        this.calculateUsagePercentage();
        this.recreateChart();
        
      } catch (error) {
        console.error('Failed to update budget:', error);
        this.budgetStatus = 'Failed to update budget on server';
      }
    },
    
    recreateChart() {
      console.log("recreatechart called");
      // Destroy and recreate chart from scratch
      if (this.budgetChart) {
        try {
          this.budgetChart.destroy();
        } catch (e) {
          console.error('Failed to destroy chart:', e);
        }
        this.budgetChart = null;
      }
      
      // Use nextTick to ensure DOM is updated
      this.$nextTick(() => {
        this.initBudgetChart();
      });
    },
    
    initBudgetChart() {
      console.log("initBudgetChart called");
      console.log(this.dailyBudget);
      console.log(this.todayEnergy);
      console.log(this.dailyBudget - this.todayEnergy);
      try {
        // Clear any existing chart to prevent errors
        if (this.budgetChart) {
          this.budgetChart.destroy();
          this.budgetChart = null;
        }
        
        const ctx = this.$refs.budgetChart;
        if (!ctx) {
          console.warn('Budget chart canvas element not found');
          return;
        }
        
        this.calculateUsagePercentage();
        
        // Create a completely minimal chart to avoid pan/zoom plugin conflicts
        this.budgetChart = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['Used', 'Remaining'],
            datasets: [{
              data: [
                this.todayEnergy, 
                Math.max(0.1, this.dailyBudget - this.todayEnergy)
              ],
              backgroundColor: [
                this.getBudgetColor(this.todayEnergy, this.dailyBudget),
                '#0f3460'  // Remaining (dark blue)
              ],
              borderWidth: 0
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                enabled: true,
                callbacks: {
                  label: function(context) {
                    const label = context.label || '';
                    const value = context.formattedValue;
                    return `${label}: ${value} kWh`;
                  }
                }
              }
            },
            // Simplify animations
            animation: {
              duration: 1000 // Longer animation duration to make it more visible
            }
          }
        });
        
        this.lastChartUpdateTime = Date.now();
        
      } catch (err) {
        console.error('Error initializing budget chart:', err);
      }
    },
    
    getBudgetColor(used, budget) {
      if (used >= budget) {
        return '#dc3545'; // Over budget (red)
      } else if (used >= budget * 0.8) {
        return '#ffc107'; // Near budget (yellow)
      } else {
        return '#28a745'; // Under budget (green)
      }
    },
    
    updateBudgetChart() {
      // Skip this function if we're not supposed to update yet
      if (this.requestCounter !== 1 && this.requestCounter % this.chartUpdateFrequency !== 0) {
        console.log(`Prevent unexpected chart update on request #${this.requestCounter}`);
        return;
      }
      
      try {
        if (!this.budgetChart || !this.budgetChart.data) {
          console.warn('Budget chart not properly initialized for update');
          return;
        }
        
        // Simply replace the entire dataset to avoid partial updates
        const usedEnergy = Math.max(0.1, this.todayEnergy || 0.1); // Ensure non-zero value
        const budgetValue = Math.max(0.1, this.dailyBudget || 5); // Ensure non-zero value
        const remainingEnergy = Math.max(0.1, budgetValue - usedEnergy); // Ensure non-zero value
        
        // Create completely new dataset object instead of modifying existing one
        this.budgetChart.data.datasets = [{
          data: [usedEnergy, remainingEnergy],
          backgroundColor: [
            this.getBudgetColor(usedEnergy, budgetValue),
            '#0f3460' // Remaining (dark blue)
          ],
          borderWidth: 0
        }];
        
        // Use the simpler update method
        try {
          this.budgetChart.update();
          console.log(`Chart successfully updated on request #${this.requestCounter}`);
        } catch (updateErr) {
          console.warn('Chart update failed, recreating chart:', updateErr);
          this.recreateChart();
        }
      } catch (err) {
        console.error('Error updating budget chart:', err);
        // Safety - recreate chart completely
        this.recreateChart();
      }
    },
    
    recreateChart() {
      if (this.budgetChart) {
        try {
          this.budgetChart.destroy();
        } catch (e) {
          console.error('Failed to destroy chart:', e);
        }
        this.budgetChart = null;
      }
      
      // Wait for next tick to ensure DOM is ready
      setTimeout(() => {
        this.initBudgetChart();
        // Don't reset request counter here, it should continue from the current value
      }, 500);
    },
  }
}
</script>

<style scoped>
.realtime-container {
  width: 100%;
  min-height: 100vh;
  background-color: #1a1a2e;
  color: #f1f1f1;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.realtime-header {
  text-align: center;
  margin-bottom: 20px;
}

.realtime-header h1 {
  color: #e94560;
  font-size: 2rem;
  margin-bottom: 5px;
}

.device-id {
  color: #aaa;
  font-size: 0.9rem;
  margin-top: 0;
}

.connection-status {
  text-align: center;
  padding: 10px;
  margin: 10px 0;
  border-radius: 8px;
  font-weight: 500;
}

.connected {
  background-color: rgba(25, 135, 84, 0.2);
  color: #28a745;
}

.disconnected {
  background-color: rgba(220, 53, 69, 0.2);
  color: #dc3545;
}

.realtime-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
  margin: 30px 0;
}

.card {
  background-color: #0f3460;
  border-radius: 12px;
  padding: 20px;
  box-sizing: border-box; /* Ensure padding is included in width */
  width: 100%;
  max-width: 300px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  text-align: center;
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
}

.energy-card {
  background-color: #16213e;
  border-left: 4px solid #e94560;
}

.money-card {
  background-color: #16213e;
  border-left: 4px solid #28a745;
}

.card h2 {
  margin-top: 0;
  color: #e94560;
  font-size: 1.4rem;
  margin-bottom: 15px;
}

.value {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
}

.back-button-container {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

.back-button {
  background-color: #e94560;
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
}

.back-button:hover {
  background-color: #d13350;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .realtime-container {
    overflow-x: hidden; /* Prevent horizontal scrolling */
  }
  
  .content {
    padding: 15px 10px; /* Reduce side padding */
    width: 100%;
    box-sizing: border-box;
  }

  .realtime-cards {
    flex-direction: column;
    align-items: center;
    gap: 15px; /* Reduce gap between cards */
    padding: 0;
    width: 100%;
  }
  
  .card {
    width: 90%; /* Limit card width */
    max-width: none; /* Override default max-width */
    padding: 15px; /* Slightly reduce padding */
    margin: 0 auto; /* Center cards */
  }
  
  .card h2 {
    font-size: 1.3rem; /* Slightly smaller heading */
  }
  
  .value {
    font-size: 1.8rem; /* Slightly smaller values */
  }
}

/* Additional breakpoint for very small screens */
@media (max-width: 380px) {
  .content {
    padding: 10px 5px;
  }

  .card {
    width: 85%; /* Even narrower on very small screens */
    padding: 12px 10px;
  }
  
  .card h2 {
    font-size: 1.2rem;
    margin-bottom: 10px;
  }
  
  .value {
    font-size: 1.6rem;
  }
}

/* New budget-related styles */
.budget-container {
  display: flex;
  justify-content: center;
  margin: 15px 0;
  padding: 0 15px;
}

.budget-input-wrapper {
  background-color: #0f3460;
  border-radius: 10px;
  padding: 15px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  min-width: 250px;
}

.budget-input-wrapper label {
  color: #e94560;
  font-weight: 500;
  margin-bottom: 8px;
  font-size: 1rem;
}

.budget-input {
  background-color: #16213e;
  border: 2px solid #2a3d62;
  border-radius: 5px;
  color: white;
  padding: 8px;
  font-size: 1.1rem;
  width: 100%;
  text-align: center;
  transition: border-color 0.3s;
}

.budget-input:focus {
  outline: none;
  border-color: #e94560;
}

/* Budget usage visualization */
.budget-usage-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 20px auto;
  max-width: 300px;
}

.doughnut-chart-container {
  position: relative;
  width: 220px;
  height: 220px;
  margin: 0 auto;
  background-color: #16213e; /* Darker background to make chart more visible */
  border-radius: 50%;
  padding: 15px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: visible;
}

canvas {
  max-width: 100%;
  max-height: 100%;
}

.budget-stats {
  margin-top: 15px;
  text-align: center;
}

.usage-percentage {
  font-size: 2.5rem;
  font-weight: 700;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.usage-label {
  color: #aaa;
  font-size: 1rem;
  margin: 5px 0;
}

.usage-values {
  color: #ddd;
  font-size: 1.1rem;
}

/* Budget status colors */
.under-budget {
  color: #28a745; /* Green */
}

.near-budget {
  color: #ffc107; /* Yellow/orange */
}

.over-budget {
  color: #dc3545; /* Red */
}

/* Responsive adjustments for budget display */
@media (max-width: 768px) {
  .budget-input-wrapper {
    width: 100%;
    max-width: 300px;
  }
  
  .doughnut-chart-container {
    width: 180px;
    height: 180px;
  }
  
  .usage-percentage {
    font-size: 2rem;
  }
}

@media (max-width: 380px) {
  .doughnut-chart-container {
    width: 150px;
    height: 150px;
  }
  
  .budget-input-wrapper {
    padding: 10px;
  }
  
  .usage-percentage {
    font-size: 1.8rem;
  }
  
  .usage-values {
    font-size: 0.9rem;
  }
}

.budget-status {
  margin-top: 8px;
  font-size: 0.9rem;
  color: #aaa;
  text-align: center;
}

.mt-2 {
  margin-top: 0.5rem;
}
</style>
