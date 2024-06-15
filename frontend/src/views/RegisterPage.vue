<template>
    <div class="container">
      <form @submit.prevent="register" >
        <h2>Registration</h2>
  
        <div class="mb-3">
          <label for="email" class="form-label">Email:</label>
          <input v-model="email" type="email" id="email" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label for="name" class="form-label">Name:</label>
          <input v-model="name" type="text" id="name" class="form-control" required />
        </div>

        <div class="mb-3">
          <label for="city" class="form-label">City:</label>
          <input v-model="city" type="text" id="city" class="form-control" required />
        </div>
  
        <div class="mb-3">
          <label for="password" class="form-label">Password:</label>
          <input v-model="password" type="password" id="password" class="form-control" required />
        </div>
        
        <div class="mb-3 form-check">
          <input v-model="isManager" type="checkbox" class="form-check-input" id="isManager" />
          <label class="form-check-label" for="isManager">Register as Manager</label>
        </div>

        <button type="submit" class="btn btn-primary">Register</button>
      </form>
    </div>
  </template>

<script>
export default {

  data() {
    return {    
      email: '',
      name: '',
      city: '',
      password: '',
      isManager: false
    }
  },
  methods: {
    async register() {
        try{
            const response = await fetch('http://localhost:5000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: this.email,
                    name: this.name,
                    city: this.city,
                    password: this.password,
                    role: this.isManager ? 'manager' : 'user'
                }),
            });
            const data = await response.json();
            if(response.ok){
                console.log(data.message);
                alert(data.message);
                this.$router.push('/login')
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

<style scoped></style>