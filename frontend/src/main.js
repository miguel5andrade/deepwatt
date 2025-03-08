import { createApp } from 'vue';
import App from './App.vue';
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { createRouter, createWebHistory } from 'vue-router'; // Import Vue Router functions


// Import components for routing
import DeviceDetailComponent from './components/DeviceDetailComponent.vue';

const app = createApp(App);

// Register the date picker component globally
app.component('vue-date-picker', VueDatePicker);

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/:macaddress',
      name: 'DeviceDetail',
      component: DeviceDetailComponent
    },
    // other routes if needed
  ]
});



// Pass the router instance to the app
app.use(router);

app.mount('#app');
