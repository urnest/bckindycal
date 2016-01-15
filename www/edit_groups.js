$(document).ready(function(){
  var saving=false;
  kc.getFromServer('groups')
    .then(function(groups){
      var $names=$('input.name');
      groups=groups||[];
      while(groups.length<4){
	groups.push({
	  name:''
	});
      };
      kc.each(groups,function(i,group){
	$($names.get(i)).prop('value',group.name);
      });
    });
  $('#save-button').click(function(){
    var groups=[];
    if (saving){
      return;
    }
    $('input.name').each(function(){
      var $name=$(this);
      var group={
	name:$name.prop('value')
      };
      groups.push(group);
    });
    saving=true;
    $('#save-button').addClass('kc-busy-cursor');
    kc.postToServer('groups',{params:kc.json.encode(groups)})
      .then(function(){
	var referer=$('input#referer').prop('value');
	if (referer){
	  window.location=referer;
	};
      })
      .always(function(){
	$('#save-button').removeClass('kc-busy-cursor');
	saving=false;
      });
    return false;
  });
});
