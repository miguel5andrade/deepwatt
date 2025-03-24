<template>
  <div class="time-selector">
    <h2 class="selector-text">Select a Time Period</h2>
    <div class="containerTimePeriod">
      <div class="datepicker-wrapper">
        <Datepicker
          v-model="internalSelectedDate"
          range
          dark
          autoApply
          :teleport="true"
          teleportTo="body"
          :enableSeconds="false"
          modelType="timestamp"
          :format="dateFormat"
          @update:model-value="onDateChange"
        />
      </div>
      <div class="buttons">
        <button @click="setLastHours(24)" :class="{ active: isLast24h }">24h</button>
        <button @click="setLastHours(12)" :class="{ active: isLast12h }">12h</button>
        <button @click="setLastHours(6)" :class="{ active: isLast6h }">6h</button>
      </div>
    </div>
    
    <div class="selected-dates">
      <span v-if="internalSelectedDate && internalSelectedDate.length > 0">
        {{ formatDate(internalSelectedDate[0]) }} to {{ formatDate(internalSelectedDate[1]) }}
      </span>
      <span v-else>Last 24h</span>
    </div>
  </div>
</template>

<script>
import Datepicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

export default {
  name: 'TimePeriodSelector',
  components: {
    Datepicker
  },
  data() {
    return {
      internalSelectedDate: [], // Use an array for the range mode
      dateFormat: 'MM/dd', // Short format for mobile
      isLast24h: true,
      isLast12h: false,
      isLast6h: false
    }
  },
  methods: {
    onDateChange(newVal) {
      if (!newVal || !Array.isArray(newVal) || newVal.length < 2) return;
      
      // Reset quick selection indicators
      this.isLast24h = false;
      this.isLast12h = false;
      this.isLast6h = false;
      
      try {
        // Convert to epoch seconds
        const epochDates = newVal.map((date) => Math.floor(new Date(date).getTime() / 1000.0));
        this.$emit('selectedDate', epochDates);
      } catch (e) {
        console.error('Error processing date values:', e);
      }
    },
    formatDate(date) {
      if (!date) return '';
      
      try {
        const timestamp = typeof date === 'number' ? date : Date.parse(date);
        const dateObj = new Date(timestamp);

        // Extract day, month, hours, and minutes
        const day = dateObj.getDate();
        const month = dateObj.getMonth() + 1; // Months are zero-based
        const hours = dateObj.getHours();
        const minutes = dateObj.getMinutes();

        // Format as dd/mm hh:mm
        return `${day.toString().padStart(2, '0')}/${month.toString().padStart(2, '0')} ${hours.toString().padStart(2, '0')}h${minutes.toString().padStart(2, '0')}`;
      } catch (e) {
        console.error('Error formatting date:', e);
        return '';
      }
    },
    setLastHours(hours) {
      // Set active state for quick selection buttons
      this.isLast24h = hours === 24;
      this.isLast12h = hours === 12;
      this.isLast6h = hours === 6;
      
      const now = new Date();
      const lastHours = new Date(now - hours * 60 * 60 * 1000);
      
      // Use fresh date objects to avoid reference issues
      this.internalSelectedDate = [lastHours.getTime(), now.getTime()];
      this.onDateChange(this.internalSelectedDate);
    }
  },
  mounted() {
    // Default to last 24 hours on mount
    this.setLastHours(24);
  }
}
</script>

<style>
.time-selector {
  width: 95%;
  max-width: 600px;
  margin: 0 auto 20px;
  border-radius: 10px;
  background-color: #0f3460;
  padding: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.datepicker-wrapper {
  flex: 1;
}

.containerTimePeriod {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Style for the buttons container */
.buttons {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 50px;
}

/* Button styling */
.buttons button {
  padding: 10px 15px;
  border: 1px solid #16213e;
  background-color: #16213e;
  color: #ddd;
  font-size: 14px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.buttons button:hover {
  background-color: #2a3d62;
  border-color: #2a3d62;
}

.buttons button.active {
  background-color: #e94560;
  border-color: #e94560;
  color: white;
  font-weight: 500;
}

.selector-text {
  text-align: center;
  font-family: 'Roboto', sans-serif;
  font-weight: 300;
  font-size: 20px;
  color: #e94560;
  margin-top: 0;
  margin-bottom: 15px;
}

.selected-dates {
  margin-top: 10px;
  text-align: center;
  font-family: 'Roboto', sans-serif;
  color: #ddd;
  font-size: 12px;
}

/* Override vue-datepicker styles for dark theme */
.dp__theme_dark {
  --dp-background-color: #16213e;
  --dp-text-color: #ddd;
  --dp-hover-color: #2a3d62;
  --dp-hover-text-color: #fff;
  --dp-hover-icon-color: #fff;
  --dp-primary-color: #e94560;
  --dp-primary-text-color: #fff;
  --dp-secondary-color: #2a3d62;
  --dp-border-color: #16213e;
  --dp-menu-border-color: #16213e;
  --dp-border-color-hover: #e94560;
  --dp-disabled-color: #666;
  --dp-scroll-bar-background: #0f3460;
  --dp-scroll-bar-color: #e94560;
  --dp-success-color: #e94560;
  --dp-success-color-disabled: #71a532;
  --dp-icon-color: #ddd;
  --dp-danger-color: #ff6562;
  --dp-highlight-color: rgba(233, 69, 96, 0.2);
}

/* Basic styling for the datepicker */
.dp__main {
  width: 100%;
}


/* Mobile layout adjustments */
@media (max-width: 600px) {
  .containerTimePeriod {
    flex-direction: column;
    gap: 10px;
  }

  .buttons {
    flex-direction: row;
    justify-content: center;
    width: 100%;
  }

  .time-selector {
    padding: 10px;
  }
  
  .selector-text {
    font-size: 16px;
    margin-bottom: 10px;
  }
  
  .selected-dates {
    font-size: 11px;
  }
  
  /* Adjust input for better mobile display */
  .dp__input {
    font-size: 12px !important;
  }
}

/* Small mobile adjustments */
@media (max-width: 400px) {
  .dp__input {
    font-size: 11px !important;
  }
}
</style>
