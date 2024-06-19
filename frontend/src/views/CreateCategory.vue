<template>
<NavBar/>
    <div class="container mt-5">
        <h1>Create Category</h1>
        <form @submit.prevent="createCategory">
            <div class="mb-3">
                <label for="name" class="form-label">Name:</label>
                <input v-model="name" type="text" id="name" class="form-control" required />
            </div>
            <button type="submit" class="btn btn-primary">Create</button>
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
            name: ''
        }
    },
    methods: {
        async createCategory() {
            try {
                const response = await fetch('http://localhost:5000/category', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    },
                    body: JSON.stringify({
                        name: this.name
                    })
                });
                const data = await response.json();
                if (response.ok) {
                    console.log(data.message);
                    alert(data.message);
                    this.$router.push('/all-categories'); // Redirect to all categories page
                } else {
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