$(document).ready(function(){
  var groups;
  var event;
  var busyCount=0;
  var $groupsOption_t=$('select.groups option').remove().first();
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
    var groups=kc.json.decode($('select.groups').prop('value'));
    var description=$('.event-description').html();
    $('body').addClass('kc-busy-cursor');
    kc.postToServer('event',{
      params:kc.json.encode({
	id:parseInt($('input#id').prop('value')),
	name:{
	  text:$('input#name').prop('value'),
	  colour:$('input#name-colour').prop('value')
	},
	groups:groups,
	dates:dates,
	description:{html:description}
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
    if (!window.confirm('Delete event?')){
      return false;
    }
    kc.postToServer('delete_event',{
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

  $('.event-description').html('');

  ++busyCount&&kc.getFromServer('groups')
    .then(function(result){
      groups=result;
      proceed();
    })
    .always(function(){
      if (--busyCount==0){
	$('body').removeClass('kc-busy-cursor');
      }
    });
  if ($('input#id').prop('value')=='0'){
    //new event
    ++busyCount&&kc.getFromServer('get_month_to_show')
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
      })
      .always(function(){
	if (--busyCount==0){
	  $('body').removeClass('kc-busy-cursor');
	}
      });
  }
  else{
    ++busyCount&&kc.getFromServer('event',
				  {id:$('input#id').prop('value')})
      .then(function(result){
	event=result;
	proceed();
      })
    .always(function(){
      if (--busyCount==0){
	$('body').removeClass('kc-busy-cursor');
      }
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
      $('select.groups').html($options);
      $('select.groups').prop('value','['+kc.join(',',event.groups)+']');
      $('input#name').prop('value',event.name.text);
      $('input#name-colour').prop('value',event.name.colour);
      $('img.name-color-picker').css('background-color',event.name.colour);
      $('div.event-description').html(event.description.html);
      tinymce.init({
	selector: 'div.event-description',
	inline: true,
	plugins: [
	  'advlist autolink lists link image charmap print preview anchor',
	  'searchreplace visualblocks code fullscreen',
	  'insertdatetime media table contextmenu paste code'
	],
	toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image'
      });
      var $dateRow_t=$('tr.date-row').remove().first();
      kc.each(event.dates,function(i,date){
	var $dateRow=$dateRow_t.clone();
	$dateRow.find('input.date').prop('value',
					 date.day+'/'+
					 date.month+'/'+
					 date.year);
	$('table.date-table').find('tr.add-date').before($dateRow);
	$dateRow.find('.delete-date').click(function(){
	  $dateRow.remove();
	  $('tr.date-row').find('.delete-date').show();
	  $('tr.date-row').find('.delete-date').first().hide();
	});
	$dateRow.find('input.date').datepicker({
	  dateFormat: 'dd/mm/yy'
	});
      });
      $('tr.date-row').find('.delete-date').show();
      $('tr.date-row').find('.delete-date').first().hide();
      $('td.add-date').click(function(){
	var $dateRow=$dateRow_t.clone();
	var today=new Date();
	$dateRow.find('input.date').prop(
	  'value',
	  today.getDate()+'/'+
	    (today.getMonth()+1)+'/'+
	    today.getFullYear());
	$('table.date-table').find('tr.add-date').before($dateRow);
	$dateRow.find('.delete-date').click(function(){
	  $dateRow.remove();
	  $('tr.date-row').find('.delete-date').show();
	  $('tr.date-row').find('.delete-date').first().hide();
	});
	$dateRow.find('input.date').datepicker({
	  dateFormat: 'd/m/yy'
	});
      });
    }
  };
});
