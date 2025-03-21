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
// Import axios for HTTP requests
import axios from 'axios';

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
      maxRetries: 5
    }
  },
  created() {
    // Get device ID from route or props
    this.deviceId = this.$route.params.macaddress || this.macaddress || '';
    console.log("RealTime component created with deviceId:", this.deviceId);
  },
  mounted() {
    this.startPolling();
  },
  beforeUnmount() {
    this.stopPolling();
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
        const response = await axios.get(`http://localhost:5501/realtime/${this.deviceId || 'default'}`);
        
        // Update data with response
        const data = response.data;
        this.current = data.rms_current || 0;
        this.power = data.rms_current * 230;
        this.todayEnergy = data.today_energy || 0;
        
        // Update connection status
        this.isConnected = true;
        this.connectionStatus = 'Connected';
        this.retryCount = 0;
        
      } catch (error) {
        this.isConnected = false;
        this.connectionStatus = 'Connection Error';
        console.error('Error fetching real-time data:', error);
        
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
    
    goBack() {
      if (this.deviceId) {
        this.$router.push(`/${this.deviceId}`);
      } else {
        this.$router.push('/');
      }
    }
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
</style>
