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
    return false;
  });
});
