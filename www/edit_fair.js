$(document).ready(function(){
  $('input.fair-date-and-time').click(function(){
    var $d=$('<div><input class="fair-date-and-time" style="width:100%" type="text"></div>');
    $d.dialog({
      modal:true,
      title:'Fair Date and Time',
      buttons:[
	{
	  text:'OK',
	  click:function(){
	    var v=$d.find('input').prop('value');
	    kc.postToServer('set-fair-date-and-time',{
	      'date-and-time':v
	    })
	      .then(function(){
		$('input.fair-date-and-time').prop('value',v);
		$d.dialog('close');
	      });
	  }
	}],
      close:function(){
	$d.dialog('destroy');
      }});
    $d.find('input').prop('value',$(this).prop('value'));
    return false;
  });
  $('input.fair-email').click(function(){
    var $d=$('<div><input class="fair-email" style="width:100%" type="text"></div>');
    $d.dialog({
      modal:true,
      title:'Fair Contact Email',
      buttons:[
	{
	  text:'OK',
	  click:function(){
	    var v=$d.find('input').prop('value');
	    kc.postToServer('set-fair-email',{
	      'email':v
	    })
	      .then(function(){
		$('input.fair-email').prop('value',v);
		$d.dialog('close');
	      });
	  }
	}],
      close:function(){
	$d.dialog('destroy');
      }});
    $d.find('input').prop('value',$(this).prop('value'));
    return false;
  });
  $('div.fair-message').click(function(){
    var $d=$('div.fair-message').clone().addClass('edit-me').css('background-color','white');
    $d.dialog({
      width:'auto',
      modal:true,
      title:'Fair Message',
      buttons:[{
	text:'OK',
	  click:function(){
	    var v=$d.html();
	    kc.postToServer('set-fair-message',{
	      'message':kc.json.encode(v)
	    })
	      .then(function(){
		$('div.fair-message').html(v);
		$d.dialog('close');
	      });
	  }
      }],
      open:function(){
	tinymce.init({
	  selector: 'div.fair-message.edit-me',
	  inline: true,
	  plugins: [
	    'advlist autolink lists link image charmap print preview anchor',
	    'searchreplace visualblocks code fullscreen',
	    'insertdatetime media table contextmenu paste code upload_doc'
	  ],
	  toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image'
	});
      },
      close:function(){
	$d.dialog('destroy');
      }});
    return false;
  });
});
