
function listclick(){
    document.getElementById('lm');
    document.querySelector('.about-model').style.display="flex";
}
function saveclose(){
  document.querySelector('.comp-reply').style.display='none';
  document.querySelector('#profile-info').style.display='block';
}
function reply(){
  document.querySelector('.comp-reply').style.display='block';
  document.querySelector('#profile-info').style.display='none';
}