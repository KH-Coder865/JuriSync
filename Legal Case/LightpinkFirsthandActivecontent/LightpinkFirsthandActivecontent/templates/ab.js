document.addEventListener('DOMContentLoaded', function () {
    const loginBtn = document.querySelector('.btn.btn-primary.ms-2');
    const loginSidebar = document.getElementById('loginSidebar');
    const overlay = document.getElementById('overlay');
    const closeBtn = document.querySelector('.close-btn');
  
    loginBtn.addEventListener('click', function (e) {
      e.preventDefault();
      loginSidebar.classList.add('open');
      overlay.classList.add('active');
    });
  
    closeBtn.addEventListener('click', function () {
      loginSidebar.classList.remove('open');
      overlay.classList.remove('active');
    });
  
    overlay.addEventListener('click', function () {
      loginSidebar.classList.remove('open');
      overlay.classList.remove('active');
    });
  });
  