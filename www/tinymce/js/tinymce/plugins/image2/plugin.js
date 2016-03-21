/**
 * plugin.js
 *
 * Released under LGPL License.
 * Copyright (c) 1999-2015 Ephox Corp. All rights reserved
 *
 * License: http://www.tinymce.com/license
 * Contributing: http://www.tinymce.com/contributing
 */

/*global tinymce:true */

tinymce.PluginManager.add('image2', function(editor) {
  function uploadImage(){
    var dom = editor.dom;
    var imgElm = editor.selection.getNode();
    var figureElm = dom.getParent(imgElm, 'figure.image');
    if (figureElm) {
      imgElm = dom.select('img', figureElm)[0];
    }
    
    if (imgElm && (imgElm.nodeName != 'IMG' || 
		   imgElm.getAttribute('data-mce-object') || 
		   imgElm.getAttribute('data-mce-placeholder'))) {
      imgElm = null;
    }
    var editImage=function($elm){
      var $dialog=$('<div>');
      var apply;
      $dialog.dialog({
	'class':'tinymce_image2_dialog',
	'close':function(){
	  if (apply){
	    apply();
	  }
	  $dialog.dialog('destroy');
	}
      });
      $('.tinymce_image2_dialog').addClass('kc-busy-cursor');
      kc.getFromServer('get_edit_image_panel')
	.then(function(result){
	  var $content=$(result);
	  $dialog.html($content);
	  $content.find('img#tinymce_image2_preview').attr(
	    'src',$elm.attr('src'));
	  $content.find('input[name="width"]').prop('value',
						    $elm.innerWidth());
	  $content.find('input[name="height"]').prop('value',
						     $elm.innerHeight());
	  $content.find('input[name="title"]').prop('value',
						    $elm.attr('title')||'');
	  var proportion=$elm.innerWidth()/$elm.innerHeight();
	  $content.find('input[name="linked"]').prop('checked',true);
	  apply=function(){
	    $elm.css({
	      width:$content.find('input[name="width"]').prop('value'),
	      height:$content.find('input[name="height"]').prop('value'),
	    });
	    $elm.attr('title',$content.find('input[name="title"]').prop('value'));
	  };
	  var applyTimer;
	  $content.find('input[name="width"]').keyPress(function(){
	    if ($content.find('input[name="linked"]').prop('checked')){
	      var w=parseInt($(this).prop('value'));
	      if (!isnan(w)){
		$content.find('input[name="height"]').prop(
		  'value',
		  w/proportion);
	      };
	    };
	    clearTimeout(applyTimer);
	    applyTimer=setTimeout(apply,50);
	  });
	  $content.find('input[name="height"]').keyPress(function(){
	    if ($content.find('input[name="linked"]').prop('checked')){
	      var h=parseInt($(this).prop('value'));
	      if (!isnan(h)){
		$content.find('input[name="width"]').prop(
		  'value',
		  w*proportion);
	      };
	    };
	    clearTimeout(applyTimer);
	    applyTimer=setTimeout(apply,50);
	  });
	  $content.find('input[name="title"]').keyPress(function(){
	    clearTimeout(applyTimer);
	    applyTimer=setTimeout(apply,50);
	  });
	  $content.find('input[name="linked"]').change(function(){
	    if ($(this).prop('checked')){
	      proportion=
		parseInt($content.find('input[name="width"]').prop('value'))/
		parseInt($content.find('input[name="height"]').prop('value'));
	    }
	  });
	})
	.always(function(result){
	  $('.tinymce_image2_dialog').removeClass('kc-busy-cursor');
	});
    };
    if (imgElm){
      $(imgElm).load(function(){
	editImage($(imgElm));
      });
    }
    else{
      kc.uploadFile($,'Choose Image')
	.then(function(url,originalFileName){
	  var data={
	    src: url,
	    alt: originalFileName,
	    title: originalFileName,
	    width: null,
	    height: null,
	    style: null
	  };
	  editor.undoManager.transact(function() {
	    var imgElm;
	    var figureElm;
	    data.id = '__mcenew';
	    editor.focus();
	    editor.selection.setContent(dom.createHTML('img', data));
	    imgElm = dom.get('__mcenew');
	    dom.setAttrib(imgElm, 'id', null);
	    if (dom.is(imgElm.parentNode, 'figure.image')) {
	      figureElm = imgElm.parentNode;
	      dom.insertAfter(imgElm, figureElm);
	      dom.remove(figureElm);
	    }
	    $(imgElm).load(function(){
	      editImage($(imgElm));
	    });
	  });
	});
    }
  };
    
  editor.addCommand('mceUploadImage2', uploadImage);
  
  editor.addButton('image2', {
    icon: 'image',
    tooltip: 'Insert/edit image',
    onclick: uploadImage,
    stateSelector: 'img:not([data-mce-object],[data-mce-placeholder]),figure.image'
  });
  
  editor.addMenuItem('image2', {
    text: 'Image',
    onclick: uploadImage,
    context: 'insert',
    prependToContext: true
  });
});
