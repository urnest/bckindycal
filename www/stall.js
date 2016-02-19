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
      '<p>Note: <input type="text" name="note"></p>'+
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
	result.then_(r.names);
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
    addPreFairHelper($a,stallName).then(function(names){
      $('.pre-fair-helper-names').text(kc.join(', ',names));
    });
    return false;
  });
});
