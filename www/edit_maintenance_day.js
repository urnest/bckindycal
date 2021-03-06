$(document).ready(function(){
  var maintenance_day;
  var rendering=kc.rendering($('div#content'));
  var busyCount=0;
  var nextVolunteerRowId=1;
  $('body').removeClass('kc-invisible');//added by kindycal.py
  $('input.date').prop('value','');
  $('input.name').prop('value','');
  $('input#save-button').click(function(){
    if (busyCount){
      return false;
    }
    $('input').removeClass('invalid-input');
    if ($('input.name').first().prop('value')==''){
      $('input.name').first().addClass('invalid-input');
      return false;
    }
    var date;
    var d=$('input.date').prop('value').split('/');
    if (d.length!=3){
      $('input.date').addClass('invalid-input');
      return false;
    }
    var maxVolunteers=parseInt($('input.max-volunteers').first().prop('value'));
    if (isNaN(parseInt(maxVolunteers))||
	maxVolunteers==0){
      $('input.max-volunteers').first().addClass('invalid-input');
      return false;
    }
    date={
      year:parseInt(d[2]),
      month:parseInt(d[1]),
      day:parseInt(d[0])
    }
    var volunteers=[];
    $('.volunteer-row').each(function(){
      var $t=$(this);
      var childs_name=$t.find('.volunteer-childs-name').prop('value');
      var parents_name=$t.find('.volunteer-parents-name').prop('value');
      var attended=$t.find('.volunteer-attended').prop('checked');
      var note=$t.find('.volunteer-note').html();
      if (childs_name||parents_name){
	volunteers.push({childs_name:childs_name,
			 parents_name:parents_name,
			 attended:attended,
			 note:note});
      }
    });
    var description=$('.job-description').html();
    $('body').addClass('kc-busy-cursor');
    ++busyCount;
    kc.postToServer('maintenance_day',{
      params:kc.json.encode({
	id:parseInt($('input#id').prop('value')),
	name:$('input.name').first().prop('value'),
	date:date,
	description:{html:description},
	maxVolunteers:maxVolunteers,
	volunteers:volunteers
      })
    })
      .then(function(){
	window.location=$('input[name="referer"]').prop('value')||'edit_events.html';
      })
      .always(function(){
	--busyCount;
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
    if (!window.confirm('Delete Maintenance Job?')){
      return false;
    }
    ++busyCount;
    kc.postToServer('delete_maintenance_day',{
      params:kc.json.encode({
	id:parseInt($('input#id').prop('value'))
      })
    })
      .then(function(){
	window.location='edit_events.html';
      })
      .always(function(){
	--busyCount;
	$('body').removeClass('kc-busy-cursor');
      });
    return false;
  });

  $('.job-description').html('');

  if ($('input#id').prop('value')=='0'){
    //new maintenance_day
    kc.getFromServer('get_month_to_show')
      .then(function(result){
	var today=new Date();
	var date={
	  'year':result.y,
	  'month':result.m,
	  'day':((result.y==today.getFullYear()&&
		  result.m==today.getMonth()+1)?today.getDate():1)
	};
	maintenance_day={
	  id:0,
	  name:'Maintenance Day 8am',
	  groups:[],
	  date:date,
	  description:{
	    html:''
	  },
	  volunteers:[
	  ]
	}
	proceed();
      });
  }
  else{
    kc.getFromServer('maintenance_day',
		     {id:$('input#id').prop('value')})
      .then(function(result){
	maintenance_day=result;
	proceed();
      });
  }
  var proceed=function(){
    if (maintenance_day){
      $('div.job-description').html(maintenance_day.description.html);
      $('div.job-description').tinymce({
	inline: true,
	plugins: [
	  'advlist autolink lists link image2 charmap print preview anchor',
	  'searchreplace visualblocks code fullscreen',
	  'insertdatetime media table contextmenu paste code upload_doc'
	],
	toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image2'
      });
      $('input.name').prop('value',maintenance_day.name);
      $('input.date').prop('value',kc.formatDate(maintenance_day.date));
      $('input.date').datepicker({
	dateFormat: 'dd/mm/yy'
      });
      $('input.max-volunteers').prop('value',maintenance_day.maxVolunteers);
      var $volunteerRow_t=$('tr.volunteer-row').remove().first();
      var addVolunteer=function(child_name,parent_name,attended,note){
	var $volunteerRow=$volunteerRow_t.clone();
	$volunteerRow.find('input.volunteer-childs-name').prop(
	  'value',
	  child_name);
	$volunteerRow.find('input.volunteer-parents-name').prop(
	  'value',
	  parent_name);
	$volunteerRow.find('input.volunteer-attended').prop(
	  'checked',
	  attended);
	$volunteerRow.find('div.volunteer-note').html(note)
	  .attr('id','volunteer-note-'+nextVolunteerRowId);
	$('table.volunteer-table').find('tr.add-volunteer').before(
	  $volunteerRow);
	$volunteerRow.find('.delete-volunteer').click(function(){
	  var name=$volunteerRow.find('input').prop('value');
	  if (name=='' || window.confirm('Remove '+name+'?')){
	    $volunteerRow.remove();
	    if ($('table.volunteer-table tr.volunteer-row').length==0){
	      $('table.volunteer-table tr').first().hide();
	    }
	  }
	  return false;
	});
	tinymce.init({
	  inline: true,
	  selector: '#volunteer-note-'+nextVolunteerRowId,
	  plugins: [
	    'advlist autolink lists link image2 charmap print preview anchor',
	    'searchreplace visualblocks code fullscreen',
	    'insertdatetime media table contextmenu paste code upload_doc'
	  ],
	  toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image2'
	});
	++nextVolunteerRowId;
	$('table.volunteer-table tr').first().show();
	return $volunteerRow;
      };
      kc.each(maintenance_day.volunteers,function(i,volunteer){
	addVolunteer(volunteer.childs_name,volunteer.parents_name,volunteer.attended,volunteer.note);
      });
      if(maintenance_day.volunteers.length==0){
	$('table.volunteer-table tr').first().hide();
      }
      $('td.add-volunteer').click(function(){
	addVolunteer('','',false,'<p></p>').find('input.volunteer-childs-name').focus();
	return false;
      });
      rendering.done();
    }
  };
});
