function go(){
    const data = document.querySelector("#template-list-item")
    let id = data.innerText.trim()
    location.href=`/userinfo/${id}`
}