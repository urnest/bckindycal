var deletePreFairHelper=function(stallName,$row){
  var name=$row.find('.helper-name').text();
  var email=$row.find('.helper-email').text();
  if (window.confirm('Remove '+name+'?')){
    kc.postToServer('delete_prefair_helper',{
      params:kc.json.encode({
	stall_name:stallName,
	helper_name:name,
	email:email})})
      .then(function(){
	$row.remove();
      });
  }
};
$(document).ready(function(){
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
  $('tr.pre-fair-helper-detail').each(function(){
    var $d=$(this);
    var stallName=$d.find('input.stall-name').prop('value');
    $d.find('a[href="delete-pre-fair-helper"]').click(function(){
      deletePreFairHelper(stallName,$d);
      return false;
    });
  });
});
