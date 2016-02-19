var addMe=function($from,stallName){
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
      '<p>and/or</p>'+
      '<p>Phone: <input type="text" name="phone"></p>'+
    '</div>');
  var add=function(name,email,phone){
    $dialog.find('input').removeClass('invalid-input');
    if (name==''){
      $dialog.find('input[name="name"]').addClass('invalid-input');
      return false;
    }
    if (email=='' && phone==''){
      $dialog.find('input[name="email"]').addClass('invalid-input');
      $dialog.find('input[name="phone"]').addClass('invalid-input');
      return false;
    }
    var alreadyDown=false;
    kc.postToServer('convenor_signup',{
      params:kc.json.encode({
	stall_name:stallName,
	name:name,
	email:email,
	phone:phone
      })
    })
      .then(function(r){
	if (!r.added){
	  alert('Sorry, someone else snuck in ahead of you :-(');
	}
	$dialog.dialog('close');
	result.then_(r.name,r.email,r.phone);
      });
  };
  $dialog.dialog({
    'width':'250px',
    'title':stallName+' Convenor',
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
	      $dialog.find('input[name="phone"]').prop('value')); 
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
	$dialog.find('input[name="phone"]').prop('value')); 
    return false;
  });
  return result;
};
$(document).ready(function(){
  var $stalls=$('div.stalls').children().filter('div');
  $stalls.each(function(){
    var $stall=$(this);
    var stallName=$stall.attr('id');
    if (!$stall.find('.stallconv a').attr('href').startsWith('mailto:')){
      var $a=$stall.find('.stallconv a');
      $a.click(function(){
	addMe($a,stallName).then(function(name,email,phone){
	  $a.attr('href','mailto:'+email);
	  $a.text(name);
	  $a.removeClass('stallconvac');
	});
	return false;
      });
    }
  });
});
