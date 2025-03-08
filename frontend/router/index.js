// router/index.js
import Vue from 'vue';
import VueRouter from 'vue-router';

import DeviceDetailComponent from '../components/DeviceDetailComponent.vue'; // Import your DeviceDetailComponent.vue

Vue.use(VueRouter);

const routes = [
  {
    path: '/:macaddress',
    name: 'DeviceDetail',
    component: DeviceDetailComponent
    
  },
  // other routes if needed
];

const router = new VueRouter({
  routes
});

export default router;
