<template>
    <NavBar/>
        <div class="container mt-5">
            <h1>Update Category</h1>
            <form @submit.prevent="updateCategory">
                <div class="mb-3">
                    <label for="name" class="form-label">Name:</label>
                    <input v-model="name" type="text" id="name" class="form-control" required />
                </div>
                <button type="submit" class="btn btn-primary">Update</button>
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
        mounted() {
            const categoryId = this.$route.params.id;
            this.fetchCategoryDetails(categoryId);
        },
        methods: {
            async fetchCategoryDetails(categoryId) {
                try {
                    const response = await fetch(`http://localhost:5000/category/${categoryId}`, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                        }
                    });
                    const data = await response.json();
                    console.log("data",data)
                    if (response.ok) {
                        this.name = data.name;
            
                    } else {
                        console.log(data.error);
                        alert(data.error);
                    }
                } catch (error) {
                    console.error(error);
                }
            },
            async updateCategory() {
                const categoryId = this.$route.params.id;
                try {
                    const response = await fetch(`http://localhost:5000/category/${categoryId}`, {
                        method: 'PUT',
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