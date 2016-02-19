$(document).ready(function(){
  var $stalls=$('div.stalls').children().filter('div');
  $stalls.each(function(){
    var $stall=$(this);
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
  });
});
