var groupPrefixes=['U1G1','U1G2','U2G1','U2G2'];
var frequencies={
  'as_required':'As Required',
  'week':'Weekly',
  'term':'Term',
  'year':'Yearly'
};
var groupsOfUnit={
  1:[0,1],
  2:[2,3]
};
var promptForName=function(){
  var $dialog=$('<form><p>Your Name: <input type="text" class="GroupName"></p></form>');
  var result={
  };
  result.then=function(f){
    result.then_=f;
  };
  $dialog.dialog({
    'title':'TWYC',
    'buttons':[
      {
	text:'Cancel',
	click:function(){ $dialog.dialog('close'); }
      },
      {
	text:'OK',
	click:function(){ result.then_($dialog.find('input').prop('value')); 
			  $dialog.dialog('close'); },
      }
    ],
    dialogClass:'kc-in-front-of-navbar'
  });
  $dialog.submit(function(){
    result.then_($dialog.find('input').prop('value')); 
    $dialog.dialog('close'); 
    return false;
  });
  return result;
};
var addMe=function($from,job,groups){
  var result={
    then_:function(){
    }
  };
  result.then=function(f){
    result.then_=f;
  }
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
      kc.postToServer('add_roster_job_volunteer',{
	params:kc.json.encode({
	  id:job.id,
	  groups:groups,
	  childs_name:childs_name,
	  parents_name:parents_name
	})
      })
	.then(function(r){
	  if (!r.added){
	    alert('Sorry, someone else snuck in ahead of you :-(');
	  }
	  job.instances=r.instances;
	  $dialog.dialog('close');
	  result.then_();
	});
  };
  $dialog.dialog({
    'title':'Your Details',
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
    dialogClass:'kc-in-front-of-navbar'
  }).show();
  $dialog.submit(function(){
    add($dialog.find('input[name="child_name"]').prop('value'),
	$dialog.find('input[name="parent_name"]').prop('value')); 
    $dialog.dialog('close'); 
    return false;
  });
  return result;
};
$(document).ready(function(){
  var groups;
  var rosterJobs;
  var groupsToShow;
  var groupsToShowOptions;
  var $groupsToShowOption_t=$('a.select-your-group').first().clone();
  var $selectYourGroup=$('a.select-your-group');
  var rendering=kc.rendering($('div#content'));
  var staff=$('body').hasClass('staff')||$('body').hasClass('admin');
  var $rosterJobsTable=$('table.roster-jobs-table');
  var $kindyWideRosterJobsTable=$('table.kindy-wide-roster-jobs-table');
  var $addMe_t=$('a[href="addme.html"]').remove().first();;
  var $job_t=$('table.roster-jobs-table tr.jobs').remove().first();
  var $kindyWideJob_t=$('table.kindy-wide-roster-jobs-table tr.jobs').remove().first();
  var unitOfGroups=function(groups){
    if (groups.length==4){
      return 0;//kindy-wide
    }
    return 1+groups[0]/2;
  };
  var groupOfGroups=function(groups){
    if (groups.length==2){
      return 0;//both
    }
    return 1+groups[0]%2;
  };
  $('body').removeClass('kc-invisible');//added by kindycal.py

  kc.getFromServer('groups')
    .then(function(result){
      groups=result;
      proceed();
    })
  kc.getFromServer('groups_to_show')
    .then(function(result){
      groupsToShow=result;
      proceed();
    })
  kc.getFromServer('roster_jobs')
    .then(function(result){
      rosterJobs=result;
      rosterJobs.sort(function(a,b){
	if (a.name<b.name){
	  return -1;
	}
	if (a.name>b.name){
	  return 1;
	}
	return 0;
      });
      proceed();
    })
  var proceed=function(){
    if (kc.defined(groups)&&
	kc.defined(groupsToShow)&&
	kc.defined(rosterJobs)){
      groupsToShowOptions=[];
      if (staff){
	groupsToShowOptions.push({text:'All',groups:[0,1,2,3]});
      };
      kc.each(groups,function(i,group){
	groupsToShowOptions.push({text:group.name,groups:[i]})
      });
      if (staff){
	// assumes 4 groups
	groupsToShowOptions.push(
	  {text:groups[0].name+' + '+groups[1].name, groups:[0,1]});
	groupsToShowOptions.push(
	  {text:groups[2].name+' + '+groups[3].name, groups:[2,3] });
	groupsToShowOptions.push(
	  {text:groups[0].name+' + '+groups[2].name, groups:[0,2] });
	groupsToShowOptions.push(
	  {text:groups[1].name+' + '+groups[3].name, groups:[1,3] });
      }
      var showGroups=function(newGroupsToShow){
	var is=kc.find(groupsToShowOptions,function(x){
	  return kc.json.encode(x.groups)==kc.json.encode(newGroupsToShow);
	});
	$('a.select-your-group').text(groupsToShowOptions[is[0]].text);
	groupsToShow=newGroupsToShow;
	kc.postToServer('groups_to_show',{
	  params:kc.json.encode(groupsToShow)
	});
	refresh();
      };
      $selectYourGroup.click(function(){
	kc.selectYourGroup('Roster Jobs - Choose Your Class',
			   groupsToShowOptions,
			   $selectYourGroup)
	  .then(showGroups);
      });
      if (!staff && groupsToShow.length!=1){
	kc.selectYourGroup('Roster Jobs - Choose Your Class',
			   groupsToShowOptions,
			   $selectYourGroup)
	  .then(showGroups);
      }
      else{
	refresh();
      }
    }
  };
  var refresh=function(){
    var groupSet={};
    kc.each(groupsToShow,function(i,g){
      groupSet[g]=true;
    });
    var i=kc.find(groupsToShowOptions,function(x){
      return kc.json.encode(x.groups)==kc.json.encode(groupsToShow);
    });
    i.push(0); //default
    $('a.select-your-group').text(groupsToShowOptions[i[0]].text);

    $rosterJobsTable.find('tr.jobs').remove();
    kc.each([1,2],function(i,unit){
      var groups=groupsOfUnit[unit];
      if (!groupSet[groups[0]]&&!groupSet[groups[1]]){
	return;
      }
      kc.each(rosterJobs,function(i,job){
	var $r;
	var c=0;
	var $addMe;
	if (job.per=='unit'){
	  $r=$job_t.clone();
	  $r.find('.unit').text('U'+unit);
	  $r.find('.group').text('G1/G2');
	    if (staff){
	      $r.find('.name').html(
		$('<a>')
		  .text(job.name)
		  .attr('href','edit_roster_job.html?id='+job.id));
	    }
	    else{
	      $r.find('.name').text(job.name);
	    }
	  $r.find('.frequency').text(frequencies[job.frequency]);
	  $r.find('.volunteers-required').text(job.volunteers_required);
	  kc.each(job.instances,function(i,instance){
	    if (kc.json.encode(groups)==kc.json.encode(instance.groups)){
	      kc.each(instance.volunteers,function(i,v){
		var $rr=$r.clone();
		if (c>0){
		  $rr.find('.unit').text('');
		  $rr.find('.group').text('');
		  $rr.find('.name').text('');
		  $rr.find('.frequency').text('');
		  $rr.find('.volunteers-required').text('');
		}
		$rr.find('.volunteer-parent-name').text(v.parents_name);
		$rr.find('.volunteer-child-name').text(v.childs_name);
		$rr.find('.volunteer-attended input').prop('checked',v.attended);
		$rr.find('.volunteer-note').html(v.note);
		$rosterJobsTable.append($rr);
		$rr.find('.volunteer-attended input').change(function(){
		  kc.postToServer('update_volunteer_attended',{
		    params:kc.json.encode({
		      id:job.id,
		      groups:groups,
		      childs_name:v.childs_name,
		      attended:$(this).prop('checked')
		    })
		  });
		});
		++c;
	      });
	    }
	  });
	  if (c<job.volunteers_required){
	    $addMe=$addMe_t.clone();
	    if (c>0){
	      $r.find('.unit').text('');
	      $r.find('.group').text('');
	      $r.find('.name').text('');
	      $r.find('.frequency').text('');
	      $r.find('.volunteers-required').text('');
	    }
	    $r.find('.volunteer-parent-name').html($addMe);
	    $addMe.click(function(){
	      addMe($addMe,
		    job,
		    groups)
		.then(function(){
		  refresh();
		});
	      return false;
	    });
	    $r.find('.volunteer-child-name').text('');
	    $r.find('.volunteer-attended').text('');
	    $r.find('.volunteer-note').text('');
	    $rosterJobsTable.append($r);
	  }
	}
      });
      kc.each([1,2],function(i,group){
	var groups=[ groupsOfUnit[unit][group-1] ];
	if (!groupSet[(unit-1)*2+group-1]){
	  return;
	}
	kc.each(rosterJobs,function(i,job){
	  var $r;
	  var c=0;
	  if (job.per=='group'){
	    $r=$job_t.clone();
	    $r.find('.unit').text('U'+unit);
	    $r.find('.group').text('G'+group);
	    if (staff){
	      $r.find('.name').html(
		$('<a>')
		  .text(job.name)
		  .attr('href','edit_roster_job.html?id='+job.id));
	    }
	    else{
	      $r.find('.name').text(job.name);
	    }
	    $r.find('.frequency').text(frequencies[job.frequency]);
	    $r.find('.volunteers-required').text(job.volunteers_required);
	    kc.each(job.instances,function(i,instance){
	      if (kc.json.encode(groups)==kc.json.encode(instance.groups)){
		kc.each(instance.volunteers,function(i,v){
		  var $rr=$r.clone();
		  if (c>0){
		    $rr.find('.unit').text('');
		    $rr.find('.group').text('');
		    $rr.find('.name').text('');
		    $rr.find('.frequency').text('');
		    $rr.find('.volunteers-required').text('');
		  }
		  $rr.find('.volunteer-parent-name').text(v.parents_name);
		  $rr.find('.volunteer-child-name').text(v.childs_name);
		  $rr.find('.volunteer-attended input').prop('checked',v.attended);
		  $rr.find('.volunteer-note').html(v.note);
		  $rosterJobsTable.append($rr);
		  $rr.find('.volunteer-attended input').change(function(){
		    kc.postToServer('update_volunteer_attended',{
		      params:kc.json.encode({
			id:job.id,
			groups:groups,
			childs_name:v.childs_name,
			attended:$(this).prop('checked')
		      })
		    });
		  });
		  ++c;
		});
	      }
	    });
	    if (c<job.volunteers_required){
	      $addMe=$addMe_t.clone();
	      if (c>0){
		$r.find('.unit').text('');
		$r.find('.group').text('');
		$r.find('.name').text('');
		$r.find('.frequency').text('');
		$r.find('.volunteers-required').text('');
	      }
	      $r.find('.volunteer-parent-name').html($addMe);
	      $addMe.click(function(){
		addMe($addMe,
		      job,
		      groups)
		  .then(function(){
		    refresh();
		  });
		return false;
	      });
	      $r.find('.volunteer-child-name').text('');
	      $r.find('.volunteer-attended').text('');
	      $r.find('.volunteer-note').text('');
	      $rosterJobsTable.append($r);
	    };
	  }
	});
      });
    });
    $kindyWideRosterJobsTable.find('tr.jobs').remove();
    kc.each(rosterJobs,function(i,job){
      var groups=[0,1,2,3];
      var $r;
      var c=0;
      var $addMe;
      if (job.per=='kindy-wide'){
	$r=$kindyWideJob_t.clone();
	if (staff){
	  $r.find('.name').html(
	    $('<a>')
	      .text(job.name)
	      .attr('href','edit_roster_job.html?id='+job.id));
	}
	else{
	  $r.find('.name').text(job.name);
	}
	$r.find('.frequency').text(frequencies[job.frequency]);
	$r.find('.volunteers-required').text(job.volunteers_required);
	kc.each(job.instances,function(i,instance){
	  if (kc.json.encode(groups)==kc.json.encode(instance.groups)){
	    kc.each(instance.volunteers,function(i,v){
	      var $rr=$r.clone();
	      if (c>0){
		$rr.find('.name').text('');
		$rr.find('.frequency').text('');
		$rr.find('.volunteers-required').text('');
	      }
	      $rr.find('.volunteer-parent-name').text(v.parents_name);
	      $rr.find('.volunteer-child-name').text(v.childs_name);
	      $rr.find('.volunteer-attended input').prop('checked',v.attended);
	      $rr.find('.volunteer-note').html(v.note);
	      $kindyWideRosterJobsTable.append($rr);
	      $rr.find('.volunteer-attended input').change(function(){
		kc.postToServer('update_volunteer_attended',{
		  params:kc.json.encode({
		    id:job.id,
		    groups:groups,
		    childs_name:v.childs_name,
		    attended:$(this).prop('checked')
		  })
		});
	      });
	      ++c;
	    });
	  }
	});
	if (c<job.volunteers_required){
	  var $addMe=$addMe_t.clone();
	  if (c>0){
	    $r.find('.name').text('');
	    $r.find('.frequency').text('');
	    $r.find('.volunteers-required').text('');
	  }
	  $r.find('.volunteer-parent-name').html($addMe);
	  $addMe.click(function(){
	    addMe($addMe,
		  job,
		  groups)
	      .then(function(){
		refresh();
	      });
	    return false;
	  });
	  $r.find('.volunteer-child-name').text('');
	  $r.find('.volunteer-attended').text('');
	  $r.find('.volunteer-note').text('');
	  $kindyWideRosterJobsTable.append($r);
	}
      }
    });
    rendering.done();
  };
});
