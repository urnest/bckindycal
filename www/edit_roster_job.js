$(document).ready(function(){
  var roster_job;
  var rendering=kc.rendering($('div#content'));
  var busyCount=0;
  var $year=$('select[name="year"]');
  var $yearOption=$year.find('option').remove().first();
  var now=new Date;
  var thisYear=now.getFullYear();
  var nextYear=thisYear+1;
  $year.append($yearOption.clone().prop('name','').text(''));
  $year.append($yearOption.clone().prop('name',''+thisYear).text(''+thisYear));
  $year.append($yearOption.clone().prop('name',''+nextYear).text(''+nextYear));
  
  $('body').removeClass('kc-invisible');//added by kindycal.py
  $('input#save-button').click(function(){
    var data={
      id:parseInt($('input[name="id"]').prop('value')),
      year:parseInt(kc.getSelectedOption($year).prop('name')),
      name:$('input[name="name"]').prop('value'),
      per:$('select[name="per"]').prop('value'),
      description:$('div.job-description').html(),
      frequency:$('select[name="frequency"]').prop('value'),
      volunteers_required:parseInt(
	$('input[name="volunteers_required"]').prop('value'))
    };
    if (busyCount){
      return false;
    }
    $('input').add($('select')).removeClass('invalid-input');
    if (data.year==''){
      $year.addClass('invalid-input');
      return false;
    }
    if (data.name==''){
      $('input[name="name"]').first().addClass('invalid-input');
      return false;
    }
    if (isNaN(data.volunteers_required)||
	(data.volunteers_required==0)){
      $('input[name="volunteers_required"]').first().addClass('invalid-input');
      return false;
    }
    ++busyCount;
    kc.postToServer('roster_job',{
      params:kc.json.encode(data)
    })
      .then(function(){
	var referer=$('input[name="referer"]').prop('value');
	window.location=referer;
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
    if ($('input[name="id"]').prop('value')=='0'){
      return false;
    }
    if (!window.confirm('Delete Roster Job?')){
      return false;
    }
    ++busyCount;
    kc.postToServer('delete_roster_job',{
      params:kc.json.encode({
	id:parseInt($('input[name="id"]').prop('value'))
      })
    })
      .then(function(){
	window.location='roster.html';
      })
      .always(function(){
	--busyCount;
	$('body').removeClass('kc-busy-cursor');
      });
    return false;
  });
  
  // note id input is set by kindycal.py edit_job_roster_page
  if ($('input[name="id"]').prop('value')=='0'){
    //new roster_job
    roster_job={
      id:0,
      year:(new Date).getFullYear(),
      name:'',
      per:'kindy-wide',
      description:'<p></p>',
      frequency:'as_required',
      volunteers_required:1
    }
    setTimeout(function(){proceed();},0);
  }
  else{
    kc.getFromServer('roster_job',
		     {id:$('input[name="id"]').prop('value')})
      .then(function(result){
	roster_job=result;
	proceed();
      });
  }
  var proceed=function(){
    if (roster_job){
      $('input[name="name"]').prop('value',roster_job.name);
      kc.selectOptionByName($year,'');
      if (roster_job.year==thisYear ||
	  roster_job.year==nextYear){
	kc.selectOptionByName($year,''+roster_job.year);
      }
      $('select[name="per"]').prop('value',roster_job.per);
      $('div.job-description').html(roster_job.description);
      $('select[name="frequency"]').prop('value',roster_job.frequency);
      $('input[name="volunteers_required"]').prop('value',roster_job.volunteers_required);
      tinymce.init({
	selector: 'div.job-description',
	inline: true,
	plugins: [
	  'advlist autolink lists link image2 charmap print preview anchor',
	  'searchreplace visualblocks code fullscreen',
	  'insertdatetime media table contextmenu paste code upload_doc'
	],
	toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image2'
      });
      rendering.done();
    }
  };
});
