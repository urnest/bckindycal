$(document).ready(function(){
  var saving=false;
  var $group_t=$('.group').remove().first();
  kc.getFromServer('groups')
    .then(function(groups){
      groups=groups||[];
      while(groups.length<4){
	groups.push({
	  name:'',
	  terms:[
	    {
	      daysOfFirstWeek:['Mon','Tue']
	    },
	    {
	      daysOfFirstWeek:['Mon','Tue','Wed']
	    },
	    {
	      daysOfFirstWeek:['Mon','Tue']
	    },
	    {
	      daysOfFirstWeek:['Mon','Tue','Wed']
	    }
	  ]
	});
      };
      kc.each(groups,function(i,group){
	var $group=$group_t.clone();
	$group.find('input[name="name"]').prop('value',group.name);
	var $term_t=$group.find('.term').remove().first();
	kc.each(group.terms,function(i,term){
	  var $term=$term_t.clone();
	  $term.find('.term-number').text(i+1);
	  $term.find('option[name="'+kc.join('-',term.daysOfFirstWeek)+'"]').prop('selected',true);
	  $group.append($term);
	});
	$('.groups').append($group);
      });
    });
  $('#save-button').click(function(){
    var groups=[];
    if (saving){
      return;
    }
    $('.group').each(function(){
      var $group=$(this);
      var group={
	name:$group.find('input[name="name"]').prop('value'),
	terms:[]
      };
      $group.find('.term').each(function(){
	var $term=$(this);
	var term={
	  daysOfFirstWeek:$term.find('select[name="days"]').prop('value').split('-')
	};
	group.terms.push(term);
      });
      groups.push(group);
    });
    saving=true;
    $('#save-button').addClass('kc-busy-cursor');
    kc.postToServer('groups',{params:kc.json.encode(groups)})
      .then(function(){
      })
      .always(function(){
	$('#save-button').removeClass('kc-busy-cursor');
	saving=false;
      });
    return false;
  });
});
