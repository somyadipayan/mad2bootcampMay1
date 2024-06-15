<template>
  <NavBar />
  <div class="home">
    <img alt="Vue logo" src="../assets/logo.png">
    <HelloWorld msg="Welcome sdfed to Your Vue.js App"/>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import HelloWorld from '@/components/HelloWorld.vue'

export default {
  name: 'HomeView',
  components: {
    HelloWorld,
    NavBar
  }
}
</script>
