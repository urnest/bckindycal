var groupPrefixes=['U1G1','U1G2','U2G1','U2G2'];
var frequencies={
  'as_required':'As Required',
  'week':'Weekly',
  'term':'Term',
  'year':'Yearly'
};
$(document).ready(function(){
  var rosterJobs;
  var rendering=kc.rendering($('div#content'));
  var staff=$('body').hasClass('staff')||$('body').hasClass('admin');
  var $rosterJobsTable=$('table.roster-jobs-table');
  var $job_t=$('table.roster-jobs-table tr.jobs').remove().first();
  var now=new Date;
  var thisYear=now.getFullYear();
  var nextYear=thisYear+1;
  var selectedJobs={} //job-id : true
  var rosterJobsSort=function(a,b){
    if (a.year<b.year){
      return -1;
    }
    if (a.year>b.year){
      return 1;
    }
    if (a.name<b.name){
      return -1;
    }
    if (a.name>b.name){
      return 1;
    }
    return 0;
  };
  $('span.year').text(''+thisYear);
  $('span.nextyear').text(''+nextYear);
  $('body').removeClass('kc-invisible');//added by kindycal.py
  
  kc.getFromServer('roster_jobs')
    .then(function(result){
      rosterJobs=result;
      rosterJobs.sort(rosterJobsSort);
      proceed();
    });
  var proceed=function(){
    if (kc.defined(rosterJobs)){
      $('.select-all').change(function(){
	var $t=$(this);
	if ($t.prop('checked')){
	  $('.selected input[type="checkbox"]').prop('checked',true);
	}
	else{
	  $('.selected input[type="checkbox"]').prop('checked',false);
	}
      });
      $('.delete-roster-jobs').click(function(){
	var s=kc.map(kc.keys(selectedJobs),function(i,id){
	  return parseInt(id);
	});
	if (s.length==0){
	  window.alert('Select one or more jobs to delete.');
	}
	else if (window.confirm('Delete selected jobs?')){
	  kc.postToServer('delete_roster_jobs',{
	    params:kc.json.encode(s)
	  })
	    .then(function(result){
	      var oldRosterJobs=rosterJobs;
	      rosterJobs=[];
	      kc.each(oldRosterJobs,function(i,job){
		if (!selectedJobs[job.id]){
		  rosterJobs.push(job);
		}
	      });
	      selectedJobs={}
	      rosterJobs.sort(rosterJobsSort);
	      refresh();
	    });
	}
	return false;
      });
      $('.copy-roster-jobs').click(function(){
	var s=kc.map(kc.keys(selectedJobs),function(i,id){
	  return parseInt(id);
	});
	if (s.length==0){
	  window.alert('select one or more jobs to copy');
	}
	else if (window.confirm('Copy selected jobs to '+nextYear+'?')){
	  kc.postToServer('copy_roster_jobs',{
	    params:kc.json.encode({jobs:s,toYear:nextYear})
	  })
	    .then(function(result){
	      selectedJobs={};
	      kc.each(result,function(i,job){
		selectedJobs[''+job.id]=true;
		rosterJobs.push(job);
	      });
	      rosterJobs.sort(rosterJobsSort);
	      refresh();
	    });
	}
	return false;
      });
      refresh();
    }
  };
  var addJobRow=function(job,thisYear,nextYear){
    var $r=$job_t.clone();
    if (job.year==thisYear){
      $r.removeClass('notthisyear');
    }
    else{
      $r.addClass('notthisyear');
    }
    $r.find('.year').text(''+job.year);
    $r.find('.per').text(job.per);
    $r.find('.name').text(job.name);
    $r.find('.frequency').text(job.frequency);
    $r.find('.volunteers-required').text(job.volunteers_required);
    $rosterJobsTable.append($r);
    $r.find('.selected input[type="checkbox"]').change(function(){
      var $t=$(this);
      if ($t.prop('checked')){
	selectedJobs[''+job.id]=true;
      }
      else{
	delete selectedJobs[''+job.id];
      }
    });
    if (selectedJobs[''+job.id]){
      $r.find('selected checkbox').prop('checked',true);
    }
  };
  var refresh=function(){
    $rosterJobsTable.find('tr.jobs').remove();
    kc.each(rosterJobs,function(i,job){
      addJobRow(job,thisYear,nextYear);
    });
    rendering.done();
  };
});
