$(document).ready(function(){
  $('.add-volunteer').click(function(){
    var id=$('input#id').prop('value');
    var $dialog=$('<div><p>Your Name: <input type="text" name="parent_name"></p><p>Your Child\'s Name: <input type="text" name="child_name"></p></div>');
    var add=function(childs_name,parents_name){
      if (parents_name==''){
	$dialog.find('input[name="parent_name"]').addClass('invalid-input');
	return false;
      }
      if (childs_name==''){
	$dialog.find('input[name="child_name"]').addClass('invalid-input');
	return false;
      }
      $dialog.find('input').removeClass('invalid-input');
      kc.postToServer('add_maintenance_day_volunteer',{
	id:id,
	childs_name:childs_name,
	parents_name:parents_name
      })
	.then(function(){
	  window.location='maintenance_day.html?id='+id;
	});
    };
    $dialog.dialog({
      'title':'Maintenance Day',
      'buttons':[
	{
	  text:'Cancel',
	  click:function(){ $dialog.dialog('close'); }
	},
	{
	  text:'OK',
	  click:function(){ 
	    add($dialog.find('input[name="child_name"]').prop('value'),
		$dialog.find('input[name="parent_name"]').prop('value')); 
	  }
	}
      ],
      close: function(){
	$dialog.dialog('destroy');
      }
    });
    return false;
  });
});
