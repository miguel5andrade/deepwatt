import { createApp } from 'vue';
import App from './App.vue';
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { createRouter, createWebHistory } from 'vue-router';

// Import components for routing
import DeviceDetailComponent from './components/DeviceDetailComponent.vue';
import RealTimeConsumption from './components/RealTimeConsumption.vue';

const app = createApp(App);

// Register the date picker component globally
app.component('vue-date-picker', VueDatePicker);

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'DefaultHome',
      component: App
    },
    {
      path: '/:macaddress',
      name: 'DeviceHome',
      component: App,
      props: true
    },
    {
      path: '/realtime/:macaddress?',
      name: 'RealTimeConsumption',
      component: RealTimeConsumption,
      props: true
    }
  ]
});

// Pass the router instance to the app
app.use(router);

app.mount('#app');
