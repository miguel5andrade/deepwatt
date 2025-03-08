<template>
  <header class="app-header">
    <div class="logo-container">
      <h1 class="brand-logo">Deep<span>Watt</span></h1>
    </div>
    <div class="header-actions">
      <!-- Any additional header actions can go here -->
    </div>
  </header>
</template>

<script>
export default {
  name: 'HeaderComponent'
}
</script>

<style scoped>
.app-header {
  background-color: #16213e;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 10;
  width: 100%;
  box-sizing: border-box;
  margin: 0;
  left: 0;
  right: 0;
}

.logo-container {
  display: flex;
  align-items: center;
}

.brand-logo {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  font-family: 'Roboto', sans-serif;
  letter-spacing: 1px;
}

.brand-logo span {
  color: #ffb347; /* Yellow/orange color for the "Watt" part */
  background: linear-gradient(45deg, #ff8a00, #ffb347);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

@media (max-width: 600px) {
  .brand-logo {
    font-size: 24px;
  }
  
  .app-header {
    padding: 12px 15px;
    width: 100vw;
    margin: 0;
    left: 0;
    right: 0;
  }
}
</style>
