$(document).ready(function(){
  var groups;
  var event;
  var $groupsOption_t=$('select.grouplst option').remove().first();
  var rendering=kc.rendering($('div#content'));
  var busyCount=0;
  var $eventHidden=$('input#event-hidden');
  var $eventVisible=$('input#event-visible');

  $('body').removeClass('kc-invisible');//added by kindycal.py

  $('input#save-button').click(function(){
    if (busyCount){
      return false;
    }
    var $name=$('input#name');
    $('input').removeClass('invalid-input');
    if ($name.prop('value')==''){
      $('input#name').addClass('invalid-input');
      return false;
    }
    if ($('input.date').first().prop('value')==''){
      $('input#dates').addClass('invalid-input');
      return false;
    }
    var dates=[];
    $('input.date').each(function(){
      var $t=$(this);
      var d=$t.prop('value').split('/');
      if (d.length!=3){
	$t.addClass('invalid-input');
	return false;
      }
      dates.push({
	year:parseInt(d[2]),
	month:parseInt(d[1]),
	day:parseInt(d[0])
      });
    });
    var hidden=$eventHidden.prop('checked');
    var groups=kc.json.decode($('select.grouplst').prop('value'));
    var description=$('.event-description').html();
    ++busyCount;
    $('body').addClass('kc-busy-cursor');
    kc.postToServer('event',{
      params:kc.json.encode({
	id:parseInt($('input#id').prop('value')),
	name:{
	  text:$('input#name').prop('value'),
	  colour:$('input#name-colour').prop('value')
	},
	hidden:hidden,
	groups:groups,
	dates:dates,
	description:{html:description}
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
  $('input#delete-button').click(function(){
    if (busyCount){
      return false;
    }
    if ($('input#id').prop('value')=='0'){
      return false;
    }
    if (!window.confirm('Delete event?')){
      return false;
    }
    ++busyCount;
    kc.postToServer('delete_event',{
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

  $('.event-description').html('');

  kc.getFromServer('groups')
    .then(function(result){
      groups=result;
      proceed();
    })
  if ($('input#id').prop('value')=='0'){
    //new event
    kc.getFromServer('get_month_to_show')
      .then(function(result){
	var today=new Date();
	var date={
	  'year':result.y,
	  'month':result.m,
	  'day':((result.y==today.getFullYear()&&
		  result.m==today.getMonth()+1)?today.getDate():1)
	};
	event={
	  id:0,
	  groups:[],
	  dates:[date],
	  name:{
	    text:'',
	    colour:'#000000'
	  },
	  description:{
	    html:''
	  }
	}
	proceed();
      });
  }
  else{
    kc.getFromServer('event',
		     {id:$('input#id').prop('value')})
      .then(function(result){
	event=result;
	proceed();
      });
  }
  var proceed=function(){
    if (groups && event){
      var $o_t=$groupsOption_t;
      var $options=$o_t.clone().prop('value','[0,1,2,3]').text('All');
      kc.each(groups,function(i,group){
	$options=$options.add($o_t.clone().prop('value','['+i+']').text(group.name));
      });
      // assumes 4 groups
      $options=$options.add($o_t.clone().prop('value','[0,1]')
			    .text(groups[0].name+'+'+groups[1].name));
      $options=$options.add($o_t.clone().prop('value','[2,3]')
			    .text(groups[2].name+'+'+groups[3].name));
      $options=$options.add($o_t.clone().prop('value','[0,2]')
			    .text(groups[0].name+'+'+groups[2].name));
      $options=$options.add($o_t.clone().prop('value','[1,3]')
			    .text(groups[1].name+'+'+groups[3].name));
      $('select.grouplst').html($options);
      $('select.grouplst').prop('value','['+kc.join(',',event.groups)+']');
      $('input#name').prop('value',event.name.text);
      $('input#name-colour').prop('value',event.name.colour);
      if (event.hidden){
	$eventHidden.prop('checked',true);
      }
      else{
	$eventVisible.prop('checked',true);
      }
      $('img.name-color-picker').css('background-color',event.name.colour);
      $('div.event-description').html(event.description.html);
      tinymce.init({
	selector: 'div.event-description',
	inline: true,
	plugins: [
	  'advlist autolink lists link image charmap print preview anchor',
	  'searchreplace visualblocks code fullscreen',
	  'insertdatetime media table contextmenu paste code upload_doc'
	],
	toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image'
      });
      var $dateRow_t=$('tr.date-row').remove().first();
      var adjustDeleteButtons=function(){
	if ($('tr.date-row').length>1){
	  $('tr.date-row').find('.delete-date').show();
	}
	else{
	  $('tr.date-row').find('.delete-date').hide();
	}
      };
      var addDate=function(date){
	var $dateRow=$dateRow_t.clone();
	$dateRow.find('input.date').prop('value',
					 date.day+'/'+
					 date.month+'/'+
					 date.year);
	$('table.date-table').find('tr.add-date').before($dateRow);
	$dateRow.find('.delete-date').click(function(){
	  $dateRow.remove();
	  adjustDeleteButtons();
	  return false;
	});
	$dateRow.find('input.date').datepicker({
	  dateFormat: 'dd/mm/yy'
	});
	return $dateRow;
      };
      kc.each(event.dates,function(i,date){
	addDate(date);
      });
      adjustDeleteButtons();
      $('td.add-date').click(function(){
	var today=new Date();
	addDate({
	  year:today.getFullYear(),
	  month:(today.getMonth()+1),
	  day:today.getDate()}).find('input').focus();
	adjustDeleteButtons();
	return false;
      });
      rendering.done();
    }
  };
});
