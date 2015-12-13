$(document).ready(function(){
  $('body').addClass('kc-busy-cursor');
  var groups;
  kc.getFromServer('groups')
    .then(function(groups){
      kc.getFromServer('groups_to_show')
	.then(function(groups_to_show){
	  var options=[];
	  // REVISIT: build options as per TODO
	})
	.always(function(){
	  $('body').removeClass('kc-busy-cursor');
	});
    })
    .or(function(e){
      alert(e);
      $('body').removeClass('kc-busy-cursor');
    });
});
