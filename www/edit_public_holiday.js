$(document).ready(function(){
  var public_holiday;
  var rendering=kc.rendering($('div#content'));
  var busyCount=0;
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
    $('body').addClass('kc-busy-cursor');
    ++busyCount;
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
    if (!window.confirm('Delete Public Holiday?')){
      return false;
    }
    ++busyCount;
    kc.postToServer('delete_public_holiday',{
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

  if ($('input#id').prop('value')=='0'){
    //new PublicHoliday
    kc.getFromServer('get_month_to_show')
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
      });
  }
  else{
    kc.getFromServer('public_holiday',
		     {id:$('input#id').prop('value')})
      .then(function(result){
	public_holiday=result;
	proceed();
      });
  }
  var proceed=function(){
    if (public_holiday){
      $('input#name').prop('value',public_holiday.name.text);
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
      kc.each(public_holiday.dates,function(i,date){
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
