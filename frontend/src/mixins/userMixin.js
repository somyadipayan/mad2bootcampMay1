export default{
    data(){
        return {
            user: null,
            role: null,
            isloggedin: false
        }
    },
    async created(){
        await this.CheckUser();
    },
    methods: {
        async CheckUser(){
            const access_token = localStorage.getItem('access_token');
            console.log(access_token);
            if(!access_token){
                this.isloggedin = false;
                console.log('no access token');
                return;
            }
            try{
                this.user = await this.getUserInfo();
                console.log("user",this.user);
                this.role = this.user.role;
                console.log("role",this.role);
                console.log("this.isloggedin",this.isloggedin); 
            }
            catch(error){
                console.log(error);
            }
            
        },
        async getUserInfo(){
            const response = await fetch('http://localhost:5000/getuserinfo', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            if (!response.ok){
                console.log('BAD RESPONSE', response)
                this.isloggedin = false;
                return null;
            }
            this.isloggedin = true;
            console.log('GOOD RESPONSE', response)
            return response.json();
        },
        logout(){
            fetch('http://localhost:5000/logout', {
                method: 'POST', 
                credentials: 'include'
            })
            .then(() => {
                localStorage.removeItem('access_token');
                this.user = null;
                this.role = null;
                this.isloggedin = false;
                this.$router.push('/login');
            })
            .catch(error => console.log(error))
        }
    }
}