$(document).ready(function(){
  var $new_password=$('input[name="new_password"]');
  var $confirm_new_password=$('input[name="confirm_new_password"]');
  $('form').submit(function(){
    var new_password=$new_password.prop('value');
    var confirm_new_password=$confirm_new_password.prop('value');
    $('.login_failed').text('');
    $new_password.removeClass('kc-invalid-input');
    if (new_password==''){
      $new_password.addClass('kc-invalid-input');
      return false;
    }
    $new_password.removeClass('kc-invalid-input');
    $confirm_new_password.removeClass('kc-invalid-input');
    if (confirm_new_password==''){
      $confirm_new_password.addClass('kc-invalid-input');
      return false;
    }
    if (new_password != confirm_new_password){
      $('.login_failed').text('passwords do not match');
      $confirm_new_password.addClass('kc-invalid-input');
      return false;
    }
    return true; // allow form submit
  });
});
