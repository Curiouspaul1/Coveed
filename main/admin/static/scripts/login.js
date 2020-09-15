// Login Handler

let admin_pass = document.getElementById('admin_pass');
let admin_id = document.getElementById('admin_id');
let submit = document.querySelector('button');

let data = {
    '_pass':admin_pass.nodeValue,
    '_id':admin_id.nodeValue
}
if (admin_id.nodeValue)
{
    submit.addEventListener('click',()=>{
        fetch('https://localhost:5000/auth/admin',{
            body:JSON.stringify(data),
            method:'POST',
            headers:{'content-type': 'application/json'},
        }).catch((err) => console.log(err));
    });
}else{
    // Extra

let sign_up = document.getElementById('sign-up');
let text = document.getElementById('headtext');

sign_up.addEventListener('click',function (){
    admin_id.style.display = 'None';
    text.innerText = 'SignUp';
    data = {
        'admin_pass':admin_pass.nodeValue,
    }
    submit.addEventListener('click',()=>{
        fetch('http://localhost:5000/admin/register',{
            body:JSON.stringify(data),
            method:'POST',
            headers:{'content-type': 'application/json'},
        }).catch((err) => console.log(err));
    });
})
}

