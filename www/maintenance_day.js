$(document).ready(function(){
  var $vrt=$('.vr-template').remove().first().removeClass('vr-template');
  var mdate=$('.mdate').first().text();
  var maintenanceDayName=$('.maintenance-day-name').first().text();
  var $addVolunteerButton=$('.add-volunteer');
  var maxVolunteers=parseInt($('input#max-volunteers').prop('value'));
  var date=kc.parseDate($('.mdate').first().text());
  if ($('.volunteer-row').length>=maxVolunteers ||
      kc.dateHasPast(date)){
    $addVolunteerButton.hide();
  }
  $addVolunteerButton.click(function(){
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
	  var $vr=$vrt.clone();
	  $vr.find('.volunteer-parent-name').text(parents_name);
	  $vr.find('.volunteer-parent-name').text(childs_name);
	  $('table.volunteers-table').append($vr);
	  $vr.show();
	  $dialog.dialog('close');
	  if ($('.volunteer-row').length>=maxVolunteers){
	    $addVolunteerButton.hide();
	  }
	});
    };
    $dialog.dialog({
      'width':'250px',
      'title':mdate+' '+maintenanceDayName,
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
