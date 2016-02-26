var addPreFairHelper=function($from,stallName){
  var result={
    then_:function(){
    }
  };
  result.then=function(f){
    result.then_=f;
  }
  var $dialog=$(
    '<div>'+
      '<p>Your Name: <input type="text" name="name"></p>'+
      '<p>Email: <input type="text" name="email"></p>'+
      '<p>Note (eg donations or handy skills): <input type="text" name="note"></p>'+
      '</div>');
  var add=function(name,email,note){
    $dialog.find('input').removeClass('invalid-input');
    if (name==''){
      $dialog.find('input[name="name"]').addClass('invalid-input');
      return false;
    }
    if (email==''){
      $dialog.find('input[name="email"]').addClass('invalid-input');
      return false;
    }
    var alreadyDown=false;
    kc.postToServer('add_prefair_helper',{
      params:kc.json.encode({
	stall_name:stallName,
	name:name,
	email:email,
	note:note
      })
    })
      .then(function(r){
	if (!r.added){
	  alert('Sorry, someone else snuck in ahead of you :-(');
	}
	$dialog.dialog('close');
	result.then_(r.names||[],r.details||[]);
      });
  };
  $dialog.dialog({
    'width':'250px',
    'title':stallName+' Pre-Fair Helper',
    'buttons':[
      {
	text:'Cancel',
	click:function(){ $dialog.dialog('close'); }
      },
      {
	text:'OK',
	click:function(){
	  add($dialog.find('input[name="name"]').prop('value'),
	      $dialog.find('input[name="email"]').prop('value'),
	      $dialog.find('input[name="note"]').prop('value')); 
	  return false;
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
    add($dialog.find('input[name="name"]').prop('value'),
	$dialog.find('input[name="email"]').prop('value'),
	$dialog.find('input[name="note"]').prop('value')); 
    return false;
  });
  return result;
};
$(document).ready(function(){
  var $stall=$('.kindycal-py-stall');
  var stallName=$stall.attr('id');
  if (!$stall.find('.stallconv a').attr('href').startsWith('mailto:')){
    var $a=$stall.find('.stallconv a');
    var f;
    f=function(){
      kc.convenorSignUp($a,stallName).then(function(name,email,phone){
	$a.attr('href','mailto:'+email);
	$a.text(name);
	$a.removeClass('stallconvac');
	$a.off('click');
      });
      return false;
    };
    $a.click(f);
  }
  $('a.add-prefair-helper').click(function(){
    addPreFairHelper($a,stallName).then(function(names,details){
      var $preFairHelperDetails=$('.pre-fair-helper-details');
      var $dt=$preFairHelperDetails.find('.pre-fair-helper-detail').remove().first();
      $('.pre-fair-helper-names').text(kc.join(', ',names));
      kc.each(details,function(i,d){
	var $d=$dt.clone().removeClass('kc-display-none');
	$d.find('.pre-fair-helper-name').text(d.name);
	$d.find('.pre-fair-helper-mailto-link')
	  .attr('href','mailto:'+d.email)
	  .text(d.email);
	$d.find('.pre-fair-helper-note').text(d.note);
	$preFairHelperDetails.append($d);
      });
      $preFairHelperDetails.append($dt);
    });
    return false;
  });
  $('.helpercell').each(function(){
    var $td=$(this);
    $(this).find('a.delete-fair-helper').click(function(){
      if (window.confirm('Delete helper?')){
	kc.postToServer('delete_stall_helper',{
	  params:kc.json.encode({
	    'helper_number':parseInt($td.find('input.helper-number').prop('value')),
	    'hour':parseInt($td.find('input.hour').prop('value')),
	    'stall_name':$td.find('input.stall-name').prop('value')
	  })})
	  .then(function(){
	    window.location.reload(true);
	  });
      }
      return false;
    });
  });
});
