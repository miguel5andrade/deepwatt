<template>
  <p>Showing details for device with MAC address: {{ macaddress }}</p>
</template>

<script>
export default {
  name: 'DeviceDetailComponent',
  data() {
    return {
      macaddress: ''
    }
  },
  mounted() {
    this.macaddress = this.$route.params.macaddress
    this.onMacAddressChange()
  },
  methods: {
    onMacAddressChange() {
      this.$emit('macaddress', this.macaddress) // Emit the macaddress to the parent component
    }
  }
}
</script>

<style>
p {
  text-align: center;
  font-family: 'Roboto', sans-serif;
  font-weight: 50;
  font-size: 10px;
}
</style>
