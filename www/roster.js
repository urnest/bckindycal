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
    'width':'250px',
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
    dialogClass:'kc-in-front-of-navbar',
    close: function(){
      $dialog.dialog('destroy');
    }
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
    var alreadyDown=false;
    kc.each(job.instances,function(i,instance){
      if (kc.json.encode(instance.groups)==kc.json.encode(groups)){
	kc.each(instance.volunteers,function(i,volunteer){
	  if (volunteer.parents_name==parents_name &&
	      volunteer.childs_name==childs_name){
	    window.alert('You are already down for this job.');
	    alreadyDown=true;
	  }
	});
      }
    });
    if (alreadyDown){
      return;
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
	  $dialog.dialog('destroy');
	  result.then_();
	});
  };
  $dialog.dialog({
    'width':'250px',
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
    dialogClass:'kc-in-front-of-navbar',
    close:function(){
      setTimeout(function(){$dialog.dialog('destroy');},0);
    },
    width: "auto"
  }).show();
  $dialog.submit(function(){
    add($dialog.find('input[name="child_name"]').prop('value'),
	$dialog.find('input[name="parent_name"]').prop('value')); 
    $dialog.dialog('close'); 
    return false;
  });
  return result;
};
var editVolunteer=function($from,job,groups,volunteer){
  var result={
    then_:function(){
    }
  };
  result.then=function(f){
    result.then_=f;
  }
  var $dialog=$(
    '<div>'+
      '  <p>Parent\'s Name: <input type="text" name="parent_name"></p>'+
      '  <p>Child\'s Name: <input type="text" name="child_name"></p>'+
      '  <p>Attended: <input type="checkbox" name="attended"></p>'+
      '  <p>Note: <div class="note edit-volunteer-note-mce"></p>'+
      '</div>');
  $dialog.find('input[name="child_name"]').prop('value',volunteer.childs_name);
  $dialog.find('input[name="parent_name"]').prop('value',volunteer.parents_name);
  $dialog.find('input[name="attended"]').prop('checked',volunteer.attended);
  $dialog.find('div.note').html(volunteer.note);
  var update=function(childs_name,parents_name,attended,note){
    if (parents_name==''){
      $dialog.find('input[name="parent_name"]').addClass('invalid-input');
      return false;
    }
    if (childs_name==''){
      $dialog.find('input[name="child_name"]').addClass('invalid-input');
      return false;
    }
    $dialog.find('input').removeClass('invalid-input');
    kc.postToServer('update_roster_job_volunteer',{
      params:kc.json.encode({
	id:job.id,
	groups:groups,
	volunteer:volunteer,
	new_volunteer:{
	  childs_name:childs_name,
	  parents_name:parents_name,
	  attended:attended,
	  note:note
	}
      })
    })
      .then(function(r){
	volunteer.parents_name=parents_name;
	volunteer.childs_name=childs_name;
	volunteer.attended=attended;
	volunteer.note=note;
	$dialog.dialog('close');
	result.then_();
      });
  };
  $dialog.dialog({
    'width':'250px',
    'title':'Edit Volunteer',
    'buttons':[
      {
	text:'Cancel',
	click:function(){ $dialog.dialog('close'); }
      },
      {
	text:'OK',
	click:function(){
	  update($dialog.find('input[name="child_name"]').prop('value'),
		 $dialog.find('input[name="parent_name"]').prop('value'),
		 $dialog.find('input[name="attended"]').prop('checked'),
		 $dialog.find('div.note').html()); 
	}
      }
    ],
    dialogClass:'kc-in-front-of-navbar',
    close:function(){
      setTimeout(function(){$dialog.dialog('destroy');},0);
    }
  });
  tinymce.init({
    selector: 'div.edit-volunteer-note-mce',
    inline: true,
    plugins: [
      'advlist autolink lists link image charmap print preview anchor',
      'searchreplace visualblocks code fullscreen',
      'insertdatetime media table contextmenu paste code upload_doc'
    ],
    toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image'
  });
  
  $dialog.submit(function(){
    add($dialog.find('input[name="child_name"]').prop('value'),
	$dialog.find('input[name="parent_name"]').prop('value')); 
    $dialog.dialog('close'); 
    return false;
  });
  return result;
};
var jobRow=function($r,staff,job,c,groups,volunteer,refresh){
  $r.find('.name a').text(job.name);
  if (staff){
    $r.find('.name a').attr('href','edit_roster_job.html?id='+job.id);
  }
  else{
    $r.find('.name a').click(function(){
      var $d=$('<div>').html(job.description);
      $d.dialog({
	title: job.name+' - Description',
	buttons:[
	  {
	    text:'Close',
	    click:function(){
	      $d.dialog('close');
	    }
	  }
	],
	close:function(){
	  $d.dialog('destroy');
	}
      });
      return false;
    });
  }
  $r.find('.frequency').text(frequencies[job.frequency]);
  $r.find('.volunteers-required').text(job.volunteers_required);
  if (c>0){
    $r.find('.name').text('');
    $r.find('.frequency').text('');
    $r.find('.volunteers-required').text('');
  }
  else{
    $r.find('.frequency').text(frequencies[job.frequency]);
    $r.find('.volunteers-required').text(job.volunteers_required);
  }
  if (!kc.defined(volunteer)){
    $r.find('.volunteer-child-name').text('');
    $r.find('.volunteer-attended').text('');
    $r.find('.volunteer-note').text('');
    return $r;
  }
  $r.find('.volunteer-parent-name').text(volunteer.parents_name);
  $r.find('.volunteer-child-name').text(volunteer.childs_name);
  $r.find('.volunteer-attended input').prop('checked',volunteer.attended);
  $r.find('.volunteer-note').html(volunteer.note);
  $r.find('.volunteer-attended input').change(function(){
    var new_attended=$(this).prop('checked');
    volunteer.attended=new_attended;
    kc.postToServer('update_roster_job_volunteer_attended',{
      params:kc.json.encode({
	id:job.id,
	groups:groups,
	volunteer:volunteer,
	new_attended:new_attended
      })
    });
  });
  $r.find('.delete-volunteer a').click(function(){
    if (window.confirm('Delete volunteer '+volunteer.parents_name+'?')){
      kc.postToServer('delete_roster_job_volunteer',{
	params:kc.json.encode({
	  id:job.id,
	  groups:groups,
	  childs_name:volunteer.childs_name
	})
      })
	.then(function(result){
	  job.instances=result;
	  refresh();
	});
    }
    return false;
  });
  $r.find('.edit-volunteer a').click(function(){
    editVolunteer($(this),job,groups,volunteer)
      .then(refresh);
    return false;
  });
  return $r;
};
var addMeRow=function($r,$addMe,staff,job,c,groups,refresh){
  jobRow($r,staff,job,c,groups);
  $r.find('.volunteer-parent-name').html($addMe);
  $r.find('.volunteer-child-name').text('');
  $r.find('.volunteer-attended').text('');
  $r.find('.volunteer-note').text('');
  $r.find('.edit-volunteer').text('');
  $r.find('.delete-volunteer').text('');
  $addMe.click(function(){
    addMe($addMe,
	  job,
	  groups)
      .then(refresh);
    return false;
  });
};
$(document).ready(function(){
  var groups;
  var rosterJobs;
  var maintenanceDays;
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
  var $mday_t=$('div.maintenance-days .Mday').remove().first();
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
  kc.getFromServer('all_maintenance_days')
    .then(function(result){
      maintenanceDays=result;
      proceed();
    })
  var proceed=function(){
    if (kc.defined(groups)&&
	kc.defined(groupsToShow)&&
	kc.defined(rosterJobs)&&
	kc.defined(maintenanceDays)){
      groupsToShowOptions=[];
      if (staff){
	groupsToShowOptions.push({text:'All',groups:[0,1,2,3]});
      };
      kc.each(groups,function(i,group){
	groupsToShowOptions.push({text:group.name,groups:[i]})
      });
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
	if (job.per=='unit'){
	  $r=$job_t.clone();
	  $r.find('.unit').text('U'+unit);
	  $r.find('.group').text('G1/G2');
	  kc.each(job.instances,function(i,instance){
	    if (kc.json.encode(groups)==kc.json.encode(instance.groups)){
	      kc.each(instance.volunteers,function(i,v){
		var $rr=$r.clone();
		$rosterJobsTable.append($rr);
		jobRow($rr,staff,job,c,groups,v,function(){
		  refresh();
		});
		$r.find('.unit').text('');
		$r.find('.group').text('');
		++c;
	      });
	    }
	  });
	  if (c<job.volunteers_required){
	    $rosterJobsTable.append($r);
	    addMeRow($r,$addMe_t.clone(),staff,job,c,groups,
		     function(){refresh();});
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
	    kc.each(job.instances,function(i,instance){
	      if (kc.json.encode(groups)==kc.json.encode(instance.groups)){
		kc.each(instance.volunteers,function(i,v){
		  var $rr=$r.clone();
		  $rosterJobsTable.append($rr);
		  jobRow($rr,staff,job,c,groups,v,function(){
		    refresh();
		  });
		  $r.find('.unit').text('');
		  $r.find('.group').text('');
		  ++c;
		});
	      }
	    });
	    if (c<job.volunteers_required){
	      $rosterJobsTable.append($r);
	      addMeRow($r,$addMe_t.clone(),staff,job,c,groups,
		       function(){refresh();});
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
      if (job.per=='kindy-wide'){
	$r=$kindyWideJob_t.clone();
	kc.each(job.instances,function(i,instance){
	  if (kc.json.encode(groups)==kc.json.encode(instance.groups)){
	    kc.each(instance.volunteers,function(i,v){
	      var $rr=$r.clone();
	      $kindyWideRosterJobsTable.append($rr);
	      jobRow($rr,staff,job,c,groups,v,function(){
		refresh();
	      });
	      ++c;
	    });
	  }
	});
	if (c<job.volunteers_required){
	  $kindyWideRosterJobsTable.append($r);
	  addMeRow($r,$addMe_t.clone(),staff,job,c,groups,
		   function(){refresh();});
	}
      }
    });
    $('div.maintenance-days').find('.Mday').remove();
    kc.each(maintenanceDays,function(i,m){
      var today=new Date();
      var id=m.id;
      var $mday=$mday_t.clone();
      var $addme=$addMe_t.clone();
      var yearToday=today.getYear()+1900;

      if (!staff){
	if (kc.dateHasPast(m.date) || m.date.year > yearToday){
	  return;
	}
      }
      $mday.find('.mdate a')
	.text(kc.formatDate(m.date))
	.attr('href',(staff?'edit_maintenance_day.html':'maintenance_day.html')+'?id='+m.id);
      $mday.find('.roster-maintenance-day-name').text(m.name);
      var names=[];
      kc.each(m.volunteers,function(i,volunteer){
	names.push(volunteer.parents_name);
      });
      if (names.length==0){
	names.push('(no volunteers yet)');
      }
      $mday.find('.mname').text(kc.join(', ',names));
      $('div.maintenance-days').append($mday);
      if (m.volunteers.length < m.maxVolunteers){
	$mday.find('.mday-addme').html($addme);
	$addme.click(function(){
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
	    kc.postToServer('add_maintenance_day_volunteer',{
	      id:id,
	      childs_name:childs_name,
	      parents_name:parents_name
	    })
	      .then(function(){
		$dialog.dialog('close');
		m.volunteers.push({
		  parents_name:parents_name,
		  childs_name:childs_name,
		  attended:false,
		  note:'<p></p>'
		});
		refresh();
	      });
	    return false;
	  };
	  $dialog.dialog({
	    'width':'250px',//for ipod/small iphone etc
	    'title':kc.formatDate(m.date)+' '+m.name,
	    'buttons':[
	      {
		text:'Cancel',
		click:function(){ 
		  $dialog.dialog('close');
		  return false;
		}
	      },
	      {
		text:'OK',
		click:function(){ 
		  add($dialog.find('input[name="child_name"]').prop('value'),
		      $dialog.find('input[name="parent_name"]').prop('value')); 
		  return false;
		}
	      }
	    ],
	    close: function(){
	      $dialog.dialog('destroy');
	    }
	  });
	  return false;
	  
	});
      }
      else{
	$mday.find('.mday-addme').text('(FULL)');
      }
    });
    rendering.done();
  };
});
