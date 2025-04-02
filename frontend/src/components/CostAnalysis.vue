<template>
  <div class="cost-analysis-container">
    <!-- Loading overlay -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="spinner"></div>
      <div class="loading-text">Loading data...</div>
    </div>

    <div class="content">
      <h1>Energy Cost Analysis</h1>
      <p class="device-id" v-if="deviceId">Device ID: {{ deviceId }}</p>
      <p class="analysis-date">Analysis for: {{ formattedDate }}</p>

      <div class="tariff-cards">
        <!-- Single Tariff -->
        <div class="tariff-card" :class="{ active: selectedTariff === 'single' }" @click="selectTariff('single')">
          <h2>Single Tariff</h2>
          <div class="input-group">
            <label>Cost per kWh</label>
            <input type="number" v-model="singleTariff.rate" step="0.001" min="0" @change="calculateCosts" />
          </div>
          <div class="cost-display">
            <p><strong>Daily Cost</strong>: {{ formatMoney(costs.single) }}</p>
          </div>
        </div>

        <!-- Bi-Tariff -->
        <div class="tariff-card" :class="{ active: selectedTariff === 'bi' }" @click="selectTariff('bi')">
          <h2>Bi-Tariff</h2>
          <div class="input-group">
            <label>Peak Hours ({{ biTariff.peakStart }}h - {{ biTariff.peakEnd }}h)</label>
            <input type="number" v-model="biTariff.peakRate" step="0.001" min="0" @change="calculateCosts" />
            <label>Off-Peak Rate ({{ biTariff.peakEnd }}h - {{ biTariff.peakStart }}h)</label>
            <input type="number" v-model="biTariff.offPeakRate" step="0.001" min="0" @change="calculateCosts" />
            <div class="time-inputs">
              <div>
                <label>Peak Start: </label>
                <input type="number" v-model="biTariff.peakStart" min="0" max="23" @change="calculateCosts" />
              </div>
              <div>
                <label>Peak End: </label>
                <input type="number" v-model="biTariff.peakEnd" min="0" max="23" @change="calculateCosts" />
              </div>
            </div>
          </div>
          <div class="cost-display">
            <p>Peak Hours Cost: {{ formatMoney(costs.biPeak) }}</p>
            <p>Off-Peak Cost: {{ formatMoney(costs.biOffPeak) }}</p>
            <p><strong>Total Daily Cost</strong>: {{ formatMoney(costs.biTotal) }}</p>
          </div>
        </div>

        <!-- Tri-Tariff -->
        <div class="tariff-card" :class="{ active: selectedTariff === 'tri' }" @click="selectTariff('tri')">
          <h2>Tri-Tariff</h2>
          <div class="input-group">
            <label>Peak Rate: </label>
            <input type="number" v-model="triTariff.peakRate" step="0.001" min="0" @change="calculateCosts" />
            <label>Mid Rate: </label>
            <input type="number" v-model="triTariff.midRate" step="0.001" min="0" @change="calculateCosts" />
            <label>Off-Peak Rate: </label>
            <input type="number" v-model="triTariff.offPeakRate" step="0.001" min="0" @change="calculateCosts" />
            <div class="time-inputs">
              <div class="time-group">
                <label>Peak Hours ({{ triTariff.peakStart }}h - {{ triTariff.peakEnd }}h)</label>
                <div class="time-field">
                  <input type="number" v-model="triTariff.peakStart" min="0" max="23" @change="calculateCosts" />
                  <span>-</span>
                  <input type="number" v-model="triTariff.peakEnd" min="0" max="23" @change="calculateCosts" />
                </div>
              </div>
              <div class="time-group">
                <label>Mid Hours ({{ triTariff.midStart }}h - {{ triTariff.midEnd }}h)</label>
                <div class="time-field">
                  <input type="number" v-model="triTariff.midStart" min="0" max="23" @change="calculateCosts" />
                  <span>-</span>
                  <input type="number" v-model="triTariff.midEnd" min="0" max="23" @change="calculateCosts" />
                </div>
              </div>
              <div class="time-group">
                <label>Off-Peak Hours: ({{ triTariff.midEnd }}h - {{ triTariff.peakStart }}h)</label>

              </div>
            </div>
          </div>
          <div class="cost-display" >
            <p>Peak Hours Cost: {{ formatMoney(costs.triPeak) }}</p>
            <p>Mid Hours Cost: {{ formatMoney(costs.triMid) }}</p>
            <p>Off-Peak Cost: {{ formatMoney(costs.triOffPeak) }}</p>
            <p><strong> Daily Cost</strong>: {{ formatMoney(costs.triTotal) }}</p>
          </div>
        </div>
      </div>

      <div class="summary-card">
        <h2>Tariff Comparison</h2>
        <div class="summary-content">
          <p class="best-option">Best Option: <span>{{ getBestTariff.name }}</span></p>
          <div class="tariff-comparison">
            <p>Single Tariff: <span>{{ formatMoney(costs.single) }}</span>
              <span v-if="costs.single > getBestTariff.cost" class="savings-potential">
                (Save {{ formatMoney(costs.single - getBestTariff.cost) }}/day)
              </span>
            </p>
            <p>Bi-Tariff: <span>{{ formatMoney(costs.biTotal) }}</span>
              <span v-if="costs.biTotal > getBestTariff.cost" class="savings-potential">
                (Save {{ formatMoney(costs.biTotal - getBestTariff.cost) }}/day)
              </span>
            </p>
            <p>Tri-Tariff: <span>{{ formatMoney(costs.triTotal) }}</span>
              <span v-if="costs.triTotal > getBestTariff.cost" class="savings-potential">
                (Save {{ formatMoney(costs.triTotal - getBestTariff.cost) }}/day)
              </span>
            </p>
          </div>
          <div class="monthly-comparison">
            <h3>Monthly Projections</h3>
            <p v-for="saving in monthlySavings" :key="saving.from">
              Switch from {{ saving.from }} to {{ saving.to }}: 
              <span class="savings">Save {{ formatMoney(saving.amount) }}</span>
            </p>
          </div>
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
export default {
  name: 'CostAnalysis',
  props: {
    macaddress: String
  },
  data() {
    return {
      deviceId: '',
      selectedTariff: 'single',
      energyData: [],
      singleTariff: {
        rate: 0.24
      },
      biTariff: {
        peakRate: 0.28,
        offPeakRate: 0.15,
        peakStart: 8,
        peakEnd: 22
      },
      triTariff: {
        peakRate: 0.32,
        midRate: 0.24,
        offPeakRate: 0.15,
        peakStart: 9,
        peakEnd: 13,
        midStart: 13,
        midEnd: 20
      },
      costs: {
        single: 0,
        biPeak: 0,
        biOffPeak: 0,
        biTotal: 0,
        triPeak: 0,
        triMid: 0,
        triOffPeak: 0,
        triTotal: 0
      },
      formattedDate: '',
      isLoading: false,
    }
  },
  async created() {
    this.deviceId = this.$route.params.macaddress || this.macaddress;
    await this.fetchData();
  },
  methods: {
    async fetchData() {
      this.isLoading = true;
      try {
        // Get yesterday's date
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        // Set to start of yesterday (00:00:00)
        yesterday.setHours(0, 0, 0, 0);
        const startTime = Math.floor(yesterday.getTime() / 1000);
        
        // Set to end of yesterday (23:59:59)
        yesterday.setHours(23, 59, 59, 999);
        const endTime = Math.floor(yesterday.getTime() / 1000);
        
        // Format date for display
        this.formattedDate = yesterday.toLocaleDateString('en-GB', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });

        const encodedId = encodeURIComponent(this.deviceId);
        const response = await fetch(
          `http://51.44.178.184:5501/data/${encodedId}?startTime=${startTime}&endTime=${endTime}`
        );
        
        if (response.ok) {
          this.energyData = await response.json();
          this.calculateCosts();
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        this.isLoading = false;
      }
    },

    selectTariff(tariff) {
      this.selectedTariff = tariff;
    },

    calculateCosts() {
      // Reset costs
      this.costs = {
        single: 0,
        biPeak: 0,
        biOffPeak: 0,
        biTotal: 0,
        triPeak: 0,
        triMid: 0,
        triOffPeak: 0,
        triTotal: 0
      };

      this.energyData.forEach((reading, index) => {
        if (index === 0) return; // Skip first reading
        
        const date = new Date(reading.timestamp * 1000);
        const hour = date.getHours();
        const energy = reading.dailyEnergy - (this.energyData[index - 1]?.dailyEnergy || 0);
        
        // Single tariff calculation
        this.costs.single += energy * this.singleTariff.rate;
        
        // Bi-tariff calculation
        if (hour >= this.biTariff.peakStart && hour < this.biTariff.peakEnd) {
          this.costs.biPeak += energy * this.biTariff.peakRate;
        } else {
          this.costs.biOffPeak += energy * this.biTariff.offPeakRate;
        }
        
        // Tri-tariff calculation
        if (hour >= this.triTariff.peakStart && hour < this.triTariff.peakEnd) {
          this.costs.triPeak += energy * this.triTariff.peakRate;
        } else if (hour >= this.triTariff.midStart && hour < this.triTariff.midEnd) {
          this.costs.triMid += energy * this.triTariff.midRate;
        } else {
          this.costs.triOffPeak += energy * this.triTariff.offPeakRate;
        }
      });

      // Calculate totals
      this.costs.biTotal = this.costs.biPeak + this.costs.biOffPeak;
      this.costs.triTotal = this.costs.triPeak + this.costs.triMid + this.costs.triOffPeak;
    },

    formatMoney(value) {
      return `${parseFloat(value).toFixed(2)} €`;
    },

    goBack() {
      this.$router.push(`/${this.deviceId}`);
    }
  },
  computed: {
    getBestTariff() {
      const tariffs = [
        { name: 'Single Tariff', cost: this.costs.single },
        { name: 'Bi-Tariff', cost: this.costs.biTotal },
        { name: 'Tri-Tariff', cost: this.costs.triTotal }
      ];
      
      return tariffs.reduce((prev, current) => 
        (current.cost < prev.cost) ? current : prev
      );
    },
    
    monthlySavings() {
      const tariffs = [
        { name: 'Single Tariff', cost: this.costs.single },
        { name: 'Bi-Tariff', cost: this.costs.biTotal },
        { name: 'Tri-Tariff', cost: this.costs.triTotal }
      ];
      
      const savings = [];
      
      // Compare each tariff with every other tariff
      for (let i = 0; i < tariffs.length; i++) {
        for (let j = 0; j < tariffs.length; j++) {
          if (i !== j && tariffs[i].cost > tariffs[j].cost) {
            savings.push({
              from: tariffs[i].name,
              to: tariffs[j].name,
              amount: (tariffs[i].cost - tariffs[j].cost) * 30
            });
          }
        }
      }
      
      // Sort by savings amount in descending order
      return savings.sort((a, b) => b.amount - a.amount);
    }
  }
}
</script>

<style scoped>
.cost-analysis-container {
  width: 100%;
  min-height: 100vh;
  background-color: #1a1a2e;
  color: #f1f1f1;
  padding: 20px;
  box-sizing: border-box;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}

h1 {
  color: #e94560;
  text-align: center;
  margin-bottom: 30px;
}

.device-id {
  text-align: center;
  color: #aaa;
  margin-bottom: 30px;
}

.analysis-date {
  text-align: center;
  color: #aaa;
  margin-bottom: 20px;
  font-style: italic;
}

.tariff-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
  width: 100%;
  box-sizing: border-box;
}

.tariff-card {
  background-color: #0f3460;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tariff-card.active {
  border: 2px solid #e94560;
  transform: translateY(-5px);
}

.tariff-card h2 {
  color: #e94560;
  margin-bottom: 20px;
  text-align: center;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-group label {
  color: #ddd;
  font-size: 0.9rem;
}

.input-group input {
  background-color: #16213e;
  border: 2px solid #2a3d62;
  border-radius: 5px;
  color: white;
  padding: 8px;
  font-size: 1rem;
}

.input-group input:focus {
  outline: none;
  border-color: #e94560;
}

.time-inputs {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

.time-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.time-field {
  display: flex;
  align-items: center;
  gap: 5px;
}

.time-field input {
  width: 50px;
  padding: 4px;
  text-align: center;
}

.time-field span {
  color: #aaa;
  font-size: 1rem;
}

.cost-display {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #2a3d62;
}

.cost-display p {
  color: #ddd;
  margin: 5px 0;
}

.back-button {
  background-color: #e94560;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 auto;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

.back-button:hover {
  background-color: #d13350;
}

/* Loading overlay styles */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(26, 26, 46, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(233, 69, 96, 0.1);
  border-left-color: #e94560;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 20px;
  color: #fff;
  font-size: 1.1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .cost-analysis-container {
    padding: 10px 5px;
  }

  .content {
    padding: 0 5px;
  }
  
  .tariff-cards {
    grid-template-columns: 1fr;
    gap: 12px;
    margin-bottom: 20px;
  }
  
  .tariff-card {
    margin: 0;
    width: calc(100% - 20px); /* Account for padding */
    padding: 12px 10px;
  }

  h1 {
    font-size: 1.5rem;
    margin-bottom: 15px;
  }

  .device-id, .analysis-date {
    font-size: 0.9rem;
    margin-bottom: 15px;
  }

  .input-group {
    gap: 8px;
  }

  .input-group input {
    font-size: 0.9rem;
    padding: 6px;
    height: 32px;
  }

  .time-field input {
    width: 36px;
    padding: 3px;
    height: 28px;
  }
}

@media (max-width: 480px) {
  .cost-analysis-container {
    padding: 5px 2px;
  }

  .content {
    padding: 0 3px;
  }

  .tariff-card {
    padding: 10px 8px;
    width: calc(100% - 16px);
  }

  .tariff-card h2 {
    font-size: 1.1rem;
    margin-bottom: 12px;
  }

  .input-group label {
    font-size: 0.8rem;
  }

  .input-group input {
    font-size: 0.8rem;
    padding: 4px;
    height: 28px;
  }

  .time-field input {
    width: 32px;
    height: 24px;
    padding: 2px;
  }

  .time-field span {
    font-size: 0.8rem;
  }

  .cost-display {
    font-size: 0.85rem;
    margin-top: 15px;
    padding-top: 15px;
  }

  .back-button {
    padding: 8px 16px;
    font-size: 0.9rem;
  }
}

.summary-card {
  background-color: #16213e;
  border-radius: 12px;
  padding: 20px;
  margin: 30px auto;
  max-width: 600px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  border-left: 4px solid #28a745;
}

.summary-card h2 {
  color: #28a745;
  text-align: center;
  margin-bottom: 20px;
  font-size: 1.4rem;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.summary-content p {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.summary-content p:last-child {
  border-bottom: none;
}

.summary-content span {
  font-weight: bold;
  color: #fff;
}

.savings {
  color: #28a745 !important;
}

.explanation {
  text-align: center;
  color: #aaa;
  font-style: italic;
  padding-top: 10px;
}

@media (max-width: 768px) {
  .summary-card {
    margin: 20px 10px;
    padding: 15px;
  }
  
  .summary-card h2 {
    font-size: 1.2rem;
  }
  
  .summary-content p {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .summary-card {
    margin: 15px 5px;
    padding: 12px;
  }
  
  .summary-content p {
    font-size: 0.85rem;
  }
}

.tariff-comparison {
  margin: 15px 0;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.savings-potential {
  color: #28a745;
  font-size: 0.9em;
  margin-left: 10px;
}

.monthly-comparison {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.monthly-comparison h3 {
  color: #e94560;
  font-size: 1.1rem;
  margin-bottom: 10px;
  text-align: center;
}

@media (max-width: 480px) {
  .savings-potential {
    display: block;
    margin-left: 0;
    margin-top: 5px;
    font-size: 0.8em;
  }
  
  .monthly-comparison h3 {
    font-size: 1rem;
  }
}
</style>
