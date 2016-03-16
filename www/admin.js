$(document).ready(function(){
  var mceInitialized=false;
  var $dialog=$('div.edit-fair-details-panel').removeClass('kc-display-none');
  var $message=$dialog.find('div.fair-message');
  var $dateAndTime=$dialog.find('input.fair-date-and-time');
  var $email=$dialog.find('input.fair-email');
  $dialog.css('background-color','white');
  $dialog.dialog({
      width:'auto',
      modal:true,
      autoOpen:false,
      title:'Fair Message',
      buttons:[{
	text:'OK',
	  click:function(){
	    var message=$message.html();
	    var dateAndTime=$dateAndTime.prop('value');
	    var email=$email.prop('value');
	    $dialog.addClass('kc-busy-cursor').find('*').addClass('kc-busy-cursor');
	    kc.postToServer('fair_details',{
	      params:kc.json.encode({
		'dateAndTime':dateAndTime,
		'email':email,
		'message':message
	      })
	    })
	      .then(function(){
		$dialog.dialog('close');
	      })
	      .always(function(){
		$dialog.removeClass('kc-busy-cursor').find('*')
		  .removeClass('kc-busy-cursor');
	      });
	  }
      }],
      open:function(){
	kc.getFromServer('fair_details')
	  .then(function(result){
	    $message.html(result.message);
	    $dateAndTime.prop('value',result.dateAndTime);
	    $email.prop('value',result.email);
	    $dialog.removeClass('kc-busy-cursor').find('*').removeClass('kc-busy-cursor');
	    if (!mceInitialized){
	      tinymce.init({
		selector: 'div.edit-fair-details-panel div.fair-message',
		inline: true,
		plugins: [
		  'advlist autolink lists link image charmap print preview anchor',
		  'searchreplace visualblocks code fullscreen',
		  'insertdatetime media table contextmenu paste code upload_doc'
		],
		toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image'
	      });
	      mceInitialized=true;
	    }
	  });
      }});
  $('a.edit-fair-details-link').click(function(){
    $dialog.dialog('open');
    $message.text('');
    $dateAndTime.prop('value','');
    $email.prop('value','');
    $dialog.addClass('kc-busy-cursor').find('*').addClass('kc-busy-cursor');
    return false;
  });
});
