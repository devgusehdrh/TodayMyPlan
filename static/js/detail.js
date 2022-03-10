// 로그아웃
function logout() {
    $.removeCookie('mytoken',{path:'/'});
    alert('로그아웃')
    window.location.replace = '/'
}


$(document).ready(function () {
    show_plan();
});


// 세부 목록 보기
function show_plan() {
    $.ajax({
        type: "get",
        url: `/detail/{{plan_no}}`,
        data: {},
        success: function (response) {
        }
    });
}

function post() {
    const myPlan = $('#textarea-post').val()

    $.ajax({
        url: "/POST/plan",
        type: "POST",
        data: {'myPlan_give': myPlan},
        success: function (response) {
            if (response['result'] == 'success') {
                alert(response['msg'])
                window.location.replace('/')
            } else {
                alert('에러 발생')
                window.location.replace('/')
            }
        }
    });
}

// 오늘 포스팅 한 플랜 삭제
function mypost_delete() {
    const unpost = confirm('오늘 계획을 정말 삭제 할까요?')
    if (unpost == true) {
        $.ajax({
            url: "/DELETE/plan",
            type: "DELETE",
            data: {},
            success: function (response) {
                if (response['result'] == 'success') {
                    alert(response['msg'])
                    window.location.replace('/')
                } else {
                    window.location.replace('/')
                }
            }
        })
    }
}

// 오늘 포스팅 한 플랜 수정
function mypost_modify() {
    const myPlan = $('#textarea-modify').val()

    $.ajax({
        url: "/PUT/plan",
        type: "PUT",
        data: {'myPlan_give': myPlan},
        success: function (response) {
            if (response['result'] == 'success') {
                alert(response['msg'])
                window.location.reload()
            } else {
                window.location.replace('/')
            }
        }
    })
}

//22.03.09 홍현승 회원정보 수정 페이지 이동
function goUserInfo(id) {
    location.href = `/userinfo/${id}`
}

//오늘 댓글 저장
function save_comment() {
    let Mycomment = $('#comment').val()

    $.ajax({
        type: "POST",
        url: `/detail/comment-registration`,
        data: {
            comment_give: Mycomment,
            plan_no_give: {{ plan_no }}
},
    success: function (response) {
        alert(response["msg"])
        window.location.reload()

    }
});
}

//댓글 삭제
function delete_comment(target) {
    //delete_comment()함수를 불러오는 버튼을 타겟으로 그 부모, 부모 div의 id값 호출
    const comment_no = $(target).parent().parent().attr("id");
    const uncomment = confirm('댓글을 정말 삭제 할까요?')
    if (uncomment == true) {
        $.ajax({
            type: "POST",
            url: `/detail/comment-delete`,
            data: {comment_no_give: comment_no, plan_no_give: {{plan_no}}},
        success: function (response) {
            alert(response["msg"])
            window.location.reload()
        }
    })
    }
}

//댓글 수정
function modify_comment(target) {
    //modify_comment()함수를 불러오는 버튼을 타겟으로 부모 div의 href값 호출
    const comment_no = $(target).parent().attr('href');

    //textarea-comment-modify + comment.comment_no의 입력값 호출
    let com_num = $('#textarea-comment-modify' + comment_no).val()

    let modification = com_num
    const modcomment = confirm('댓글을 정말 수정 할까요?')

    if (modcomment == true) {
        $.ajax({
            type: "PUT",
            url: `/detail/comment-modify`,
            data: {
                comment_no_give: comment_no,
                modcomment_give: modification,
                plan_no_give: {{ plan_no }}
    },
        success: function (response) {
            alert(response["msg"])
            window.location.reload()
        }
    })
    }
}