var monthNames=['January','February','March','April','May','June','July','August','September','October','November','December'];
var dayNames=['SUNDAY','MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY'];
var dayIndices={
  'Sun':0,
  'Mon':1,
  'Tue':2,
  'Wed':3,
  'Thu':4,
  'Fri':5,
  'Sat':6,
  'Sun':7
};
var $calendar;
var $week_t;
var $sunday_t;
var $weekday_t;
var $saturday_t;
var $event_t;
function prevMonth(m){
  if (m.m==1){
    return {
      'y':m.y-1,
      'm':12
    }
  }
  return {
    'y':m.y,
    'm':m.m-1
  }
};
function nextMonth(m){
  if (m.m==12){
    return {
      'y':m.y+1,
      'm':1
    }
  }
  return {
    'y':m.y,
    'm':m.m+1
  }
};
$(document).ready(function(){
  var groups;
  var terms;
  var groupsToShow;
  var busyCount=0;
  var $groupsToShowOption_t=$('select.groups-to-show option').remove().first();
  var monthToShow={
    y: new Date().getFullYear(),
    m: new Date().getMonth()+1
  };
  $calendar=$('table.month-of-events');
  $event_t=$calendar.find('span.event').remove().first();
  $week_t=$calendar.find('tr.week').remove().first();
  
  $('body').addClass('kc-busy-cursor');
  ++busyCount&&kc.getFromServer('groups')
    .then(function(result){
      groups=result;
      proceed();
    })
    .always(function(e){
      if (--busyCount){
	$('body').removeClass('kc-busy-cursor');
      }
    });
  ++busyCount&&kc.getFromServer('groups_to_show')
    .then(function(result){
      groupsToShow=result;
      proceed();
    })
    .always(function(){
      if (--busyCount==0){
	$('body').removeClass('kc-busy-cursor');
      }
    });
  ++busyCount&&kc.getFromServer('terms')
    .then(function(result){
      terms=result;
      proceed();
    })
    .always(function(){
      if (--busyCount){
	$('body').removeClass('kc-busy-cursor');
      }
    });
  var proceed=function(){
    if (kc.defined(groups)&&
	kc.defined(terms)&&
	kc.defined(groupsToShow)){
      var $o_t=$groupsToShowOption_t;
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
      $('select.groups-to-show').html($options);
      $('select.groups-to-show').prop('value','['+kc.join(',',groupsToShow)+']');
      $('select.groups-to-show').change(function(){
	setTimeout(function(){
	  groupsToShow=kc.json.decode($('select.groups-to-show').prop('value'));
	  kc.postToServer('groups_to_show',{
	    params:kc.json.encode(groupsToShow)
	  });
	  refresh();
	},0);
      });
      $('a.prevmonth').click(function(){
	monthToShow=prevMonth(monthToShow);
	refresh();
	return false;
      });
      $('a.nextmonth').click(function(){
	monthToShow=nextMonth(monthToShow);
	refresh();
	return false;
      });
      refresh();
    }
  };
  var refresh=function(){
    var cal;
    var events;
    $('span.month').text(monthNames[monthToShow.m]);
    $('span.year').text(monthToShow.y);
    kc.getFromServer('month_calendar',{params:kc.json.encode(monthToShow)})
      .then(function(result){
	cal=result;
	proceed();
      });
    kc.getFromServer('month_events',monthToShow)
      .then(function(result){
	events={};
	kc.each(result,function(i,event){
	  kc.each(event.dates,function(i,ymd){
	    if (ymd.year==monthToShow.y&&
		ymd.month==monthToShow.m){
	      events[ymd.day]=events[ymd.day]||[];
	      events[ymd.day].push(event);
	    }
	  });
	});
	proceed();
      });
    var proceed=function(){
      if (kc.defined(cal)&&kc.defined(events)){
	$calendar.find('tr.week').remove();
	kc.each(cal.weeks,function(i,week){
	  var $week=$week_t.clone();
	  var $days=$week.find('td.day');
	  var weekName='';
	  var groupDay=[false,false,false,false,false,false,false]
	  if (week.term_week){
	    var oddWeek=(week.term_week.week%2)!=0;
	    kc.each(groupsToShow,function(i,group){
	      kc.each(groups[group].terms[week.term_week.term-1].daysOfFirstWeek,function(i,shortDayName){
		if (shortDayName=='Wed'){
		  if (oddWeek){
		    groupDay[dayIndices[shortDayName]]=true;
		  }
		}
		else{
		  groupDay[dayIndices[shortDayName]]=true;
		}
	      });
	      if (groups[group].terms[week.term_week.term-1].daysOfFirstWeek.length==2 && !oddWeek){
		groupDay[3]=true;
	      }
	    });
	    if (week.term_week.week==1){
	      weekName='Term '+week.term_week.term+
		'<br>week '+week.term_week.week;
	    }
	    else{
	      weekName='week '+week.term_week.week;
	    }
	  }
	  $week.find('.week-label').html(weekName);
	  kc.each(week.days,function(i,day){
	    var $day=$($days.get(i));
	    $day.find('span.day').text(day||'');
	    if (groupDay[i]){
	      $day.removeClass('calout').addClass('calon');
	    }
	    else{
	      $day.removeClass('calon').addClass('calout');
	    }
	  });
	  $calendar.append($week);
	});
      }
    };
  };
});
