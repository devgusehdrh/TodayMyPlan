function onLogin(){
    const id = document.getElementById("ID").value
    const pw = document.getElementById("PW").value


    $.ajax({
        type: 'POST',
        url: '/login_check',
        data: {user_id: id, password:  pw},
        success: function (response) {

            if(response['result'] == 'success'){

                $.cookie('mytoken', response['token'], {path: '/'});
                window.location.replace("/")
            }else{
                console.log(response["msg"])
            }
        }
    });

}

function goSignUp(){

}