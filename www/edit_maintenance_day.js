$(document).ready(function(){
  var maintenance_day;
  var busyCount=0;
  $('input.date').prop('value','');
  $('input#save-button').click(function(){
    if (busyCount){
      return false;
    }
    $('input').removeClass('invalid-input');
    if ($('input.date').first().prop('value')==''){
      $('input#date').first().addClass('invalid-input');
      return false;
    }
    var date;
    var d=$('input.date').prop('value').split('/');
    if (d.length!=3){
      $('input.date').addClass('invalid-input');
      return false;
    }
    date={
      year:parseInt(d[2]),
      month:parseInt(d[1]),
      day:parseInt(d[0])
    }
    var volunteers=[];
    if (!$('volunteer-childs-name').each(function(){
      var $t=$(this);
      if ($t.prop('value')==''){
	$t.addClass('invalid-input');
	return false;
      }
      volunteers.push({childs_name:$t.prop('value')});
    })){
      return false;
    }
    var description=$('.maintenance-day-description').html();
    $('body').addClass('kc-busy-cursor');
    kc.postToServer('maintenance_day',{
      params:kc.json.encode({
	id:parseInt($('input#id').prop('value')),
	date:date,
	description:{html:description},
	volunteers:volunteers
      })
    })
      .then(function(){
	window.location='edit_events.html';
      })
      .always(function(){
	$('body').removeClass('kc-busy-cursor');
      });
    return false;
  });
  $('input#delete-button').click(function(){
    if (busyCount){
      return false;
    }
    if ($('input#id').prop('value')=='0'){
      return false;
    }
    if (!window.confirm('Delete Maintenance Day?')){
      return false;
    }
    kc.postToServer('delete_maintenance_day',{
      params:kc.json.encode({
	id:parseInt($('input#id').prop('value'))
      })
    })
      .then(function(){
	window.location='edit_events.html';
      })
      .always(function(){
	$('body').removeClass('kc-busy-cursor');
      });
    return false;
  });

  $('.maintenance-day-description').html('');

  if ($('input#id').prop('value')=='0'){
    //new maintenance_day
    var today=new Date();
    maintenance_day={
      id:0,
      groups:[],
      date:{
	year: today.getFullYear(),
	month: today.getMonth()+1,
	day: today.getDate()
      },
      description:{
	html:'(click to edit)'
      },
      volunteers:[
      ]
    }
    setTimeout(function(){proceed();},0);
  }
  else{
    ++busyCount&&kc.getFromServer('maintenance_day',
				  {id:$('input#id').prop('value')})
      .then(function(result){
	maintenance_day=result;
	proceed();
      })
    .always(function(){
      if (--busyCount==0){
	$('body').removeClass('kc-busy-cursor');
      }
    });
  }
  var proceed=function(){
    if (maintenance_day){
      $('div.maintenance-day-description').html(maintenance_day.description.html);
      tinymce.init({
	selector: 'div.maintenance-day-description',
	inline: true,
	plugins: [
	  'advlist autolink lists link image charmap print preview anchor',
	  'searchreplace visualblocks code fullscreen',
	  'insertdatetime media table contextmenu paste code'
	],
	toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image'
      });
      $('input.date').prop('value',kc.formatDate(maintenance_day.date));
      $('input.date').datepicker({
	dateFormat: 'dd/mm/yy'
      });
      var $volunteerRow_t=$('tr.volunteer-row').remove().first();
      kc.each(maintenance_day.volunteers,function(i,volunteer){
	var $volunteerRow=$volunteerRow_t.clone();
	$volunteerRow.find('input.volunteer-childs-name').prop(
	  'value',
	  volunteer.childs_name);
	$('table.volunteer-table').append($volunteerRow);
	$volunteerRow.find('.delete-volunteer').click(function(){
	  $volunteerRow.remove();
	  $('tr.volunteer-row').find('.delete-volunteer').show();
	  $('tr.volunteer-row').find('.delete-volunteer').first().hide();
	});
      });
      $('table.volunteer-table').append(
	$('table.volunteer-table').find('tr.add-volunteer').remove());
      $('tr.volunteer-row').find('.delete-volunteer').show();
      $('td.add-volunteer').click(function(){
	var $volunteerRow=$volunteerRow_t.clone();
	$volunteerRow.find('input.volunteer-childs-name').prop('value','');
	$('table.volunteer-table').append($volunteerRow);
	$volunteerRow.find('.delete-volunteer').click(function(){
	  $volunteerRow.remove();
	  $('tr.volunteer-row').find('.delete-volunteer').show();
	});
	$('table.volunteer-table').append(
	  $('table.volunteer-table').find('tr.add-volunteer').remove());
      });
    }
  };
});
