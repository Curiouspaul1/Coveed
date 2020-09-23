// Login Handler

let admin_pass = document.getElementById('admin_pass');
let admin_id = document.getElementById('admin_id');
let signin = document.getElementById('signin');
let signup = document.getElementById('signup');
let sign_up = document.getElementById('sign-up');
let text = document.getElementById('headtext');

signup.style.display = 'None';

function SignIn(data)
{
    fetch('http://localhost:5000/auth/admin',{
        body:JSON.stringify(data),
        method:'POST',
        headers:{'content-type': 'application/json'},
    }).then(resp => {
        return resp.json()
    }).then(resp => {
        console.log(resp)
    }).catch((err) => console.log(err));
}

function SignUp(data)
{
    console.log(data);
    fetch('http://localhost:5000/admin/register',{
        body:JSON.stringify(data),
        method:'POST',
        headers:{'content-type': 'application/json'},
    }).then(resp => {
        return resp.json()
    }).then(resp => {
        console.log(resp)
    }).catch((err) => console.log(err));
}


signin.addEventListener('click',function (){
    admin_pass = document.getElementById('admin_pass');
    admin_id = document.getElementById('admin_id');
    if (admin_id)
    {
        let data = {
            '_pass':admin_pass.value,
            '_id':admin_id.value
        }
        console.log(data);
        SignIn(data);
    }
});

sign_up.addEventListener('click',function (){
    admin_id.style.display = 'None';
    sign_up.style.display = 'None';
    text.innerText = 'SignUp';
    signin.style.display = 'None';
    let switch_ = document.getElementById('switch');
    switch_.style.marginTop = '80px';
    signup.style.display='block';
    
    signup.addEventListener('click',function (){
        admin_pass = document.getElementById('admin_pass');
        data = {
            'admin_pass':admin_pass.value,
        }
        SignUp(data);
    });
})

