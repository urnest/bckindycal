$(document).ready(function(){
  var saving=false;
  kc.getFromServer('terms')
    .then(function(result){
      var terms;
      var today=new Date();
      result=result||{'numberOfTerms':4,'terms':[]};
      terms=result.terms;
      while(terms.length<result.numberOfTerms){
	terms.push({
	  start:{
	    year: today.getYear()+1900,
	    month: today.getMonth()+1,
	    day: today.getDay()
	  },
	  end:{
	    year: today.getYear()+1900,
	    month: today.getMonth()+1,
	    day: today.getDay()
	  }
	});
      }
      var $term_t=$('.term').remove().first();
      kc.each(terms,function(i,term){
	var $t=$term_t.clone();
	$t.find('.term-number').text(i+1);
	$t.find('.start').attr('value',kc.formatDate(term.start));
	$t.find('.end').attr('value',kc.formatDate(term.end));
	$('.terms').append($t);
      });
    });
  $('#save-button').click(function(){
    var $terms=$('.term');
    var params={
      numberOfTerms:0,
      terms:[]
    };
    if (saving){
      return;
    }
    saving=true;
    $terms.each(function(){
      var $t=$(this);
      var start=$t.find('.start').prop('value').split('/');
      var end=$t.find('.end').prop('value').split('/');
      ++params.numberOfTerms;
      params.terms.push({
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
    $('#save-button').addClass('kc-busy-cursor');
    kc.postToServer('terms',{params:kc.json.encode(params)})
      .then(function(){
      })
      .always(function(){
	$('#save-button').removeClass('kc-busy-cursor');
	saving=false;
      });
    return false;
  });
});
