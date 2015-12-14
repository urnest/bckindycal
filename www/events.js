var monthNames=['January','February','March','April','May','June','July','August','September','October','November','December'];
var dayNames=['SUNDAY','MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY'];

$(document).ready(function(){
  var groups;
  var terms;
  var groupsToShow;
  var busyCount=1;
  var $groupsToShowOption_t=$('select.groups-to-show option').remove().first();
  var monthToShow={
    y: new Date().getFullYear(),
    m: new Date().getMonth()+1
  };
  $('body').addClass('kc-busy-cursor');
  kc.getFromServer('groups')
    .then(function(result){
      groups=result;
      proceed();
    })
    .always(function(e){
      if (--busyCount){
	$('body').removeClass('kc-busy-cursor');
      }
    });
  kc.getFromServer('groups_to_show')
    .then(function(result){
      groupsToShow=result;
      proceed();
    })
    .always(function(){
      if (--busyCount){
	$('body').removeClass('kc-busy-cursor');
      }
    });
  kc.getFromServer('terms')
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
      var $options=$o_t.clone().prop('value','[]').text('All');
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
	groupsToShow=kc.json.decode($('select.groups-to-show').prop('value'));
	kc.postToServer('groups_to_show',groupsToShow);
	refresh();
      });
      refresh();
    }
  };
  var refresh=function(){
    kc.getFromServer('getcal',monthToShow,function(result){
    });
  };
});
