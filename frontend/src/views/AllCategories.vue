<template>
    <NavBar />
    <div class="container mt-5">
        <h1>All Categories</h1>
        <div v-if="categories.length > 0">
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th v-if="this.role==='admin'">Created By</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="category in categories" :key="category.id">
                    <td>{{ category.id }}</td>
                    <td>{{ category.name }}</td>
                    <td v-if="this.role==='admin'">{{ category.creator_email }}</td>
                    <td  v-if="this.role==='admin'">
                    <button v-if="!category.verified" class="btn btn-light" @click="verifyCategory(category.id)">Verify</button>
                    <button v-else class="btn btn-light" disabled>Verified</button>
                    </td>
                    <td class="btn-group">
                        <button @click="viewCategory(category.id)" class="btn btn-light">View</button>
                        <router-link v-if="this.role==='admin'||this.role==='manager'" :to="{ name: 'update-category', params: { id: category.id } }" class="btn btn-light">Update</router-link>
                        <!-- Below is an alternative to above -->
                        <!-- <router-link v-if="this.role==='admin'||this.role==='manager'" :to="`/update-category/${category.id}`" class="btn btn-light">Update</router-link> -->
                        <button v-if="this.role==='admin'" @click="deleteCategory(category.id)" class="btn btn-light">Delete</button>
                    </td>
                </tr>
            </tbody>  
            </table>
            </div>
            <div v-else>
                <p>No categories found.</p>
            </div>
            <router-link  v-if="this.role==='admin'||this.role==='manager'" :to="{ name: 'create-category' }" class="btn btn-primary">Create a new Category</router-link>
    </div> 
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import userMixin from '@/mixins/userMixin';
export default {
    components: {
        NavBar
    },
    mixins: [userMixin],
    data() {
        return {
            categories: [],
        }
    },
    async created() {
        await this.getAllCategories();
    },
    methods: {
        async getAllCategories() {
            try {
                const response = await fetch('http://localhost:5000/categories', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                const data = await response.json();
                this.categories = data;
            } catch (error) {
                console.error(error);
            }
        },
        async deleteCategory(id) {
            try{
                const response = await fetch(`http://localhost:5000/category/${id}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
                const data = await response.json();
                if (response.ok) {
                    console.log(data.message);
                    alert(data.message);
                    this.getAllCategories();
                } else {
                    console.log(data.error);
                    alert(data.error);
                }
            }catch(error){
                console.error(error);s
            }
        },
        viewCategory(id){
        console.log('VIEWING CATEGORY', id);
        },

        async verifyCategory(id) {
            try {
                const response = fetch(`http://localhost:5000/verify-category/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
                });
                const data = await response.json();
                if (response.ok) {
                    console.log(data.message);
                    alert(data.message);
                    this.getAllCategories();
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
