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
});
