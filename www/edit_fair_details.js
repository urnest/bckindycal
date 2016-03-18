$(document).ready(function(){
  var mceInitialized=false;
  var $content=$('div#content');
  var $message=$content.find('div.fair-message');
  var $dateAndTime=$content.find('input.fair-date-and-time');
  var $email=$content.find('input.fair-email');
  $content.find('input[type="submit"]').click(function(){
    var message=$message.html();
    var dateAndTime=$dateAndTime.prop('value');
    var email=$email.prop('value');
    $content.addClass('kc-busy-cursor').find('*').addClass('kc-busy-cursor');
    kc.postToServer('fair_details',{
      params:kc.json.encode({
	'dateAndTime':dateAndTime,
	'email':email,
	'message':message
      })
    })
      .then(function(){
	window.location=$('input[name="referer"]').prop('value');
      })
      .always(function(){
	$content.removeClass('kc-busy-cursor').find('*').removeClass('kc-busy-cursor');
      });
  });
  
  tinymce.init({
    selector: 'div#content div.fair-message',
    inline: true,
    plugins: [
      'advlist autolink lists link image charmap print preview anchor',
      'searchreplace visualblocks code fullscreen',
      'insertdatetime media table contextmenu paste code upload_doc'
    ],
    toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image'
  });
});
