//파일 추가에 이벤트리스너 달아주기
const fileInput = document.querySelector('.file-label input[type=file]');
fileInput.onchange = (e) => {
    if (fileInput.files.length > 0) {
        const fileName = document.querySelector('.file-name');
        fileName.textContent = fileInput.files[0].name;
        readImage(e.target)
    }
}


//이미지 파일 읽기
function readImage(input) {
    // 인풋 태그에 파일이 있는 경우
    if (input.files && input.files[0]) {
        // 이미지 파일인지 검사 (생략)
        // FileReader 인스턴스 생성
        const reader = new FileReader()
        // 이미지가 로드가 된 경우
        reader.onload = e => {
            const previewImage = document.getElementById("preview-image")
            previewImage.src = e.target.result
        }
        // reader가 이미지 읽도록 하기
        reader.readAsDataURL(input.files[0])
    }
}

//로그아웃
function sign_out() {
    $.removeCookie('mytoken', {path: '/'});
    alert('로그아웃!')
    window.location.href = "/login"
}

//프로필 수정 모달 보이기
function showEditModal() {
    const modal = document.getElementById("edit-modal")
    modal.style.display = "flex"
}

//비번 수정 모달 보이기
function showPwModal() {
    const modal = document.getElementById("pw-modal")
    modal.style.display = "flex"
}

//프로필 수정 모달 닫기
function closeEditModal() {
    const modal = document.getElementById("edit-modal")
    modal.style.display = "none"
}

//비번 수정 모달 닫기
function closePwModal() {
    const modal = document.getElementById("pw-modal")
    modal.style.display = "none"
}

//프로필 수정 변경
function onEditInfo() {
    const nickName = document.getElementById("edit-nickName").value
    const greeting = document.getElementById("edit-greeting").value
    const file = document.getElementById("file").files[0]


    if (nickName.trim().length !== 0) {
        const form_data = new FormData()
        form_data.append("file", file)
        form_data.append("nickName", nickName)
        form_data.append("greeting", greeting)

        $.ajax({
            type: "POST",
            url: "/editInfo",
            data: form_data,
            cache: false,
            contentType: false,
            processData: false,
            success: function (response) {
                closeEditModal()
                location.reload()
            }
        });
    }

}

//비번 변경
function onChangePw() {
    const pw = document.getElementById("help-password")
    const chkPw = document.getElementById("help-password2")

    if (pw.classList.contains("is-success") && chkPw.classList.contains("is-success")) {
        const password = document.getElementById("pw").value
        $.ajax({
            type: 'POST',
            url: '/editPw',
            data: {password: password},
            success: function (response) {
                closePwModal()
                location.reload()

            }
        });
    }
}

//확인 비번 입력검증
function chkRePw() {
    const password = document.getElementById("pw").value
    const password2 = document.getElementById("chkPw").value
    if (password2 == "") {
        $("#help-password2").text("비밀번호를 입력해주세요.").removeClass("is-success").addClass("is-danger")
        $("#chkPw").focus()
        return;
    } else if (password2 != password) {
        $("#help-password2").text("비밀번호가 일치하지 않습니다.").removeClass("is-success").addClass("is-danger")
        $("#chkPw").focus()
        return;
    } else {
        $("#help-password2").text("비밀번호가 일치합니다.").removeClass("is-danger").addClass("is-success")
    }
}

//비번 입력 검증
function checkPw() {
    const password = document.getElementById("pw").value

    if (password == "") {
        $("#help-password").text("비밀번호를 입력해주세요.").removeClass("is-success").addClass("is-danger")
        $("#pw").focus()
        return;
    } else if (!is_password(password)) {
        $("#help-password").text("비밀번호의 형식을 확인해주세요. 영문과 숫자 필수 포함, 특수문자(!@#$%^&*) 사용가능 8-20자").removeClass("is-safe").addClass("is-danger")
        $("#pw").focus()
        return
    } else {
        $("#help-password").text("사용할 수 있는 비밀번호입니다.").removeClass("is-danger").addClass("is-success")
    }

}

//비밀번호 규칙검증
function is_password(asValue) {
    var regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;
    return regExp.test(asValue);
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
                    window.location.reload()
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