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
var $public_holiday_t;
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
  var monthToShow;
  $calendar=$('table.month-of-events');
  $event_t=$calendar.find('div.event').remove().first();
  $public_holiday_t=$calendar.find('div.public-holiday').remove().first();
  
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
  ++busyCount&&kc.getFromServer('get_month_to_show')
    .then(function(result){
      monthToShow=result;
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
	kc.defined(groupsToShow)&&
	kc.defined(monthToShow)){
      var $o_t=$groupsToShowOption_t;
      var $options=$o_t.clone().prop('value','[0,1,2,3]').text('All');
      kc.each(groups,function(i,group){
	$options=$options.add($o_t.clone().prop('value','['+i+']').text(group.name));
      });
      // assumes 4 groups
      $options=$options.add($o_t.clone().prop('value','[0,1]')
			    .text(groups[0].name+' + '+groups[1].name));
      $options=$options.add($o_t.clone().prop('value','[2,3]')
			    .text(groups[2].name+' + '+groups[3].name));
      $options=$options.add($o_t.clone().prop('value','[0,2]')
			    .text(groups[0].name+' + '+groups[2].name));
      $options=$options.add($o_t.clone().prop('value','[1,3]')
			    .text(groups[1].name+' + '+groups[3].name));
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
	kc.postToServer('remember_month',monthToShow);
	refresh();
	return false;
      });
      $('a.nextmonth').click(function(){
	monthToShow=nextMonth(monthToShow);
	kc.postToServer('remember_month',monthToShow);
	refresh();
	return false;
      });
      refresh();
    }
  };
  var refresh=function(){
    var cal;
    var events;
    var public_holidays;
    var maintenance_days;
    $('span.month').text(monthNames[monthToShow.m-1]);
    $('span.year').text(monthToShow.y);
    kc.getFromServer('month_calendar',{params:kc.json.encode(monthToShow)})
      .then(function(result){
	cal=result;
	proceed();
      });
    kc.getFromServer('month_events',monthToShow)
      .then(function(result){
	events=result;
	proceed();
      });
    kc.getFromServer('month_public_holidays',monthToShow)
      .then(function(result){
	public_holidays=result;
	proceed();
      });
    kc.getFromServer('month_maintenance_days',monthToShow)
      .then(function(result){
	maintenance_days=result;
	proceed();
      });
    var proceed=function(){
      var groupSet={};
      if (kc.defined(cal) &&
	  kc.defined(events) &&
	  kc.defined(public_holidays) &&
	  kc.defined(maintenance_days)){
	kc.each(groupsToShow,function(i,g){
	  groupSet[g]=true;
	});
	$calendar.find('tr.week').remove();
	var dateDays={};
	kc.each(cal.weeks,function(i,week){
	  var $week=$week_t.clone();
	  var $days=$week.find('td.day');
	  var weekName='';
	  var dayClass=['','','','','','','']
	  var dayClasses=['','','','','','',''];
	  if (week.term_week){
	    var oddWeek=(week.term_week.week%2)!=0;
	    var termStartsWith=terms.terms[week.term_week.term-1].starts_with;
	    if ((oddWeek && termStartsWith=='mon-wed')||
		(!oddWeek && termStartsWith=='mon-tue')){
	      dayClasses=['','mon-wed','mon-wed','mon-wed','wed-fri','wed-fri',''];
	    }
	    else {
	      dayClasses=['','mon-wed','mon-wed','wed-fri','wed-fri','wed-fri',''];
	    }
	    if (week.term_week.week==1){
	      weekName='Term '+week.term_week.term+
		'<br>Week '+week.term_week.week;
	    }
	    else{
	      weekName='Week '+week.term_week.week;
	    }
	  }
	  $week.find('.week-label').html(weekName);
	  kc.each(week.days,function(i,day){
	    var $day=$($days.get(i));
	    $day.removeClass('public-holiday');
	    $day.find('span.day').text(day||'');
	    if (day){
	      dateDays[day]=$day;
	    }
	    else{
	      $day.addClass('other-month');
	    }
	    $day.removeClass('mon-wed').removeClass('wed-fri');
	    if (dayClasses[i]){
	      $day.addClass(dayClasses[i]);
	    }
	  });
	  $calendar.append($week);
	});
	kc.each(events,function(i,event){
	  var show=false;
	  kc.each(event.groups,function(i,g){
	    if (groupSet[g]){
	      show=true;
	    }
	  });
	  if (!show){
	    return;
	  }
	  kc.each(event.dates,function(i,date){
	    if (date.year==monthToShow.y&&
		date.month==monthToShow.m&&
		dateDays[date.day]){
	      var $event=$event_t.clone();
	      $event.find('.event-link').attr('href','event.html?id='+event.id);
	      $event.find('.event-link').text(event.name.text);
	      $event.find('.event-link').css('color',event.name.colour);
	      
	      dateDays[date.day].append($event);
	    }
	  });
	});
	kc.each(public_holidays,function(i,public_holiday){
	  kc.each(public_holiday.dates,function(i,date){
	    if (date.year==monthToShow.y&&
		date.month==monthToShow.m&&
		dateDays[date.day]){
	      var $public_holiday=$public_holiday_t.clone();
	      $public_holiday.find('.public-holiday-name').text(
		public_holiday.name.text);
	      $public_holiday.find('.public-holiday-link').attr(
		'href','edit_public_holiday.html?id='+public_holiday.id);
	      dateDays[date.day].append($public_holiday);
	      dateDays[date.day].addClass('public-holiday');
	    }
	  });
	});
	kc.each(maintenance_days,function(i,event){
	  var date=event.date;
	  if (date.year==monthToShow.y&&
	      date.month==monthToShow.m&&
	      dateDays[date.day]){
	    var $event=$event_t.clone();
	    $event.find('.event-link').attr('href','maintenance_day.html?id='+event.id);
	    $event.find('.event-link').text(event.name);
	    dateDays[date.day].append($event);
	  }
	});
      }
    };
  };
});
