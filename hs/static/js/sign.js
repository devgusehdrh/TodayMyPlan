function onSign(){
    const id = document.getElementById("id").value
    const pw = document.getElementById("pw").value
    const nickName = document.getElementById("nicknName").value


    $.ajax({
        type: 'POST',
        url: '/signup',
        data: {user_id: id, password:  pw, nickName:nickName},
        success: function (response) {
            if(response.msg ){
                location.href = '/login'
            }
        }
    });

}