$(document).ready(function(){
  $('.add-volunteer').click(function(){
    var id=$('input#id').prop('value');
    var $dialog=$('<p>Your Child\'s Name: <input type="text"></p>');
    var add=function(childs_name){
      if (childs_name==''){
	$dialog.find('input').addClass('invalid-input');
	return false;
      }
      $dialog.find('input').removeClass('invalid-input');
      kc.postToServer('add_maintenance_day_volunteer',{
	id:id,
	childs_name:childs_name
      })
	.then(function(){
	  window.location='maintenance_day.html?id='+id;
	});
    };
    $dialog.dialog({
      'buttons':{
	'OK':function(){ add($dialog.find('input').prop('value')); },
	'Cancel':function(){ $dialog.dialog('close'); }
      }
    }).show();
    return false;
  });
});
