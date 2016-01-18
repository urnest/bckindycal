$(document).ready(function(){
  var public_holiday;
  var busyCount=0;
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
    $('body').addClass('kc-busy-cursor');
    kc.postToServer('public_holiday',{
      params:kc.json.encode({
	id:parseInt($('input#id').prop('value')),
	name:{
	  text:$('input#name').prop('value')
	},
	dates:dates
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
    if (!window.confirm('Delete Public Holiday?')){
      return false;
    }
    kc.postToServer('delete_public_holiday',{
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

  if ($('input#id').prop('value')=='0'){
    //new PublicHoliday
    ++busyCount&&kc.getFromServer('get_month_to_show')
      .then(function(result){
	var today=new Date();
	var date={
	  'year':result.y,
	  'month':result.m,
	  'day':((result.y==today.getFullYear()&&
		  result.m==today.getMonth()+1)?today.getDate():1)
	};
	public_holiday={
	  id:0,
	  dates:[date],
	  name:{
	    text:''
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
    ++busyCount&&kc.getFromServer('public_holiday',
				  {id:$('input#id').prop('value')})
      .then(function(result){
	public_holiday=result;
	proceed();
      })
    .always(function(){
      if (--busyCount==0){
	$('body').removeClass('kc-busy-cursor');
      }
    });
  }
  var proceed=function(){
    if (public_holiday){
      $('input#name').prop('value',public_holiday.name.text);
      var $dateRow_t=$('tr.date-row').remove().first();
      kc.each(public_holiday.dates,function(i,date){
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
