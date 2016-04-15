$(document).ready(function(){
  $('.kindycal-py-link').each(function(){
    var $t=$(this);
    var link={
      title:$t.find('.kindycal-py-title').text(),
      url:$t.find('.kindycal-py-url').text(),
      description:$t.find('.kindycal-py-description').text()
    };
    $t.find('.kindycal-py-title').append(
      $('<span> <a class="staff-only link-delete" title="Remove" href="remove-link"><i class="fa fa-trash-o fa-fw"></i></a>'));
    $t.find('.kindycal-py-title').find('a.link-delete').click(function(){
      if (window.confirm('Delete "'+link.title+'" link?')){
	kc.postToServer('delete_link',{
	  params:kc.json.encode(link)
	})
	  .then(function(){$t.remove();});
      }
      return false;
    });
  });
  var $addLink=$('.add-link');
  var $linkPanel=$('.link-panel').hide();
  var $linkTitle=$linkPanel.find('.link-title');
  var $linkURL=$linkPanel.find('.link-url');
  var $linkDescription=$linkPanel.find('.link-description');
  kc.trackTextInput($linkTitle,function(title){
    if (title==''){
      $linkTitle.addClass('kc-invalid-input');
    }
    else{
      $linkTitle.removeClass('kc-invalid-input');
    }
  });
  kc.trackTextInput($linkURL,function(title){
    if (title==''){
      $linkURL.addClass('kc-invalid-input');
    }
    else{
      $linkURL.removeClass('kc-invalid-input');
    }
  });
  $addLink.find('a').click(function(){
    $addLink.hide('blind');
    $linkPanel.show('fade');
    $linkTitle.prop('value','').addClass('kc-invalid-input');
    $linkURL.prop('value','').addClass('kc-invalid-input');
    $linkDescription.prop('value','');
    return false;
  });
  $linkPanel.find('.link-panel-ok').click(function(){
    var link={
      'title':$linkTitle.prop('value'),
      'url':$linkURL.prop('value'),
      'description':$linkDescription.prop('value')
    };
    if ((link.title != '') && (link.url != '')){
      kc.postToServer('add_link',{
	params:kc.json.encode(link)
      })
	.then(function(){
	  window.location.reload();
	});
    }
    return false;
  });
  $('body').removeClass('kc-invisible');//added by kindycal.py
})
