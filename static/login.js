document.querySelector('.signIn').addEventListener('click', function(event) {
    if(event.target === document.querySelector(".signUpBtn")){
    this.style.display = 'none';
    document.querySelector('.signUp').style.display = 'block';
    }
})

document.querySelector('.signUp').addEventListener('click', function(event) {
    if(event.target === document.querySelector(".signInBtn")){
        this.style.display = 'none';
        document.querySelector('.signIn').style.display = 'block';
        } 
})
