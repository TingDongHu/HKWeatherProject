function saveStorage(id) {
    var data=new Object;
    data.name=document.getElementById("name").value;
    data.password=document.getElementById("password").value;
    data.phone=document.getElementById("phone").value;
    data.email=document.getElementById("email").value; 
    //手机验证
    let reg_phone=/^[1][35789][\d]{9}$/;//表示必须以13/17/18/19开头，11位
    if(data.phone===''){
     document.getElementById(id).innerHTML="手机号不能为空！";
     return false;
    }else if(!reg_phone.test(data.phone)){
     document.getElementById(id).innerHTML="手机号不正确！";
     return false;
    } 
    //邮箱验证 它只允许域名部分由字母、数字或下划线组成 它只允许顶级域名和二级域名只包含小写字母。
    let reg_email=/^([a-zA-Z1-9][\w-]{2,})@(\w{2,})\.([a-z]{2,})(\.[a-z]{2,})?$/;
    if(data.email!==''){
    if(!reg_email.test(data.email)){
     document.getElementById(id),innerHTML='邮箱格式不正确';
     return false;
    }}
    //提交数据
    let str = JSON.stringify(data);
    localStorage.setItem(data.name,str)
    document.getElementById(id).innerHTML="注册成功";
    setTimeout(function(){
     document.location.href="/login/"
    },5000)

    return false;
 //    document.getElementById(id).innerHTML="测试";
 //    alert(data.name)
 }
 