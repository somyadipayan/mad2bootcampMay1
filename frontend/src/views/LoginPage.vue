<template>
    <NavBar />
    <div class="container">
      <form @submit.prevent="login" >
        <h2>Login Here</h2>
  
        <div class="mb-3">
          <label for="email" class="form-label">Email:</label>
          <input v-model="email" type="email" id="email" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label for="password" class="form-label">Password:</label>
          <input v-model="password" type="password" id="password" class="form-control" required />
        </div>
    
        <button type="submit" class="btn btn-primary">Login</button>
      </form>
    </div>
  </template>

<script>
import NavBar from '@/components/NavBar.vue';
export default {
    components: {
        NavBar
    },
    data() {
        return {
            email: '',
            password: ''
        }
    },
    methods: {
        async login() {
            try{
            const response = await fetch('http://localhost:5000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: this.email,
                    password: this.password,
                }),
            });
            const data = await response.json();
            if(response.ok){
                console.log(data.message);
                localStorage.setItem('access_token', data.access_token);
                alert(data.message);
                this.$router.push('/')
            }
            else{
                console.log(data.error);
                alert(data.error);
            }
        } catch (error) {
            console.error(error);
        }
        }
    }
}

</script>