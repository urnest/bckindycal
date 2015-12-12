$(document).ready(function(){
  var saving=false;
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
      }
      var $group_t=$('.group').remove().first();
      kc.each(groups,function(i,group){
	var $group=$group_t.clone();
	$group.find('.name').attr('value',group.name);
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
    //REVISIT
    var $groups=$('.group');
    var params={
      numberOfGroups:0,
      groups:[]
    };
    if (saving){
      return;
    }
    saving=true;
    $groups.each(function(){
      var $t=$(this);
      var start=$t.find('.start').prop('value').split('/');
      var end=$t.find('.end').prop('value').split('/');
      ++params.numberOfGroups;
      params.groups.push({
	start:{
	  day: parseInt(start[0]),
	  month: parseInt(start[1]),
	  year: parseInt(start[2])
	},
	end:{
	  day: parseInt(end[0]),
	  month: parseInt(end[1]),
	  year: parseInt(end[2])
	}
      });
    });
    saving=true;
    $('#save-button').addClass('busy');
    kc.postToServer('groups',{params:kc.json.encode(params)})
      .then(function(){
      })
      .always(function(){
	$('#save-button').removeClass('busy');
	saving=false;
      });
    return false;
  });
});
