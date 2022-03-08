const fileInput = document.querySelector('.file-label input[type=file]');
fileInput.onchange = (e) => {
    if (fileInput.files.length > 0) {
        const fileName = document.querySelector('.file-name');
        fileName.textContent = fileInput.files[0].name;
        readImage(e.target)
    }
}


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

function sign_out() {
    $.removeCookie('mytoken', {path: '/'});
    alert('로그아웃!')
    window.location.href = "/login"
}

function showEditModal() {
    const modal = document.getElementById("edit-modal")
    modal.style.display = "flex"
}

function showPwModal() {
    const modal = document.getElementById("pw-modal")
    modal.style.display = "flex"
}

function closeEditModal() {
    const modal = document.getElementById("edit-modal")
    modal.style.display = "none"
}

function closePwModal() {
    const modal = document.getElementById("pw-modal")
    modal.style.display = "none"
}

function onEditInfo() {
    let nickName = document.getElementById("edit-nickName").value
    let greeting = document.getElementById("edit-greeting").value
    let file = document.getElementById("file").files[0]
    let form_data = new FormData()
    console.log(greeting)
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
            location.reload()
        }
    });
}
