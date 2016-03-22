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
      var apply=function(){};
      $dialog.dialog({
	modal:true,
	'title':'Edit Image',
	'dialogClass':'tinymce_image2_dialog',
	'close':function(){
	  apply();
	  apply=function(){};
	  $dialog.dialog('destroy');
	},
	'open':function(){
	  // bring dialog in front of image resize handles, which are
	  // at 10000
	  $('.tinymce_image2_dialog').css('z-index',20000);
	}
      });
      $('.tinymce_image2_dialog').addClass('kc-busy-cursor');
      kc.getFromServer('get_edit_image_panel')
	.then(function(result){
	  var $content=$(result);
	  var $width=$content.find('input[name="width"]');
	  var $height=$content.find('input[name="height"]');
	  var $title=$content.find('input[name="title"]');
	  var $linked=$content.find('input[name="linked"]');
	  var $preview=$content.find('img#tinymce_image2_preview');
	  var $changeImage=$content.find('.change-image-button');
	  $dialog.html($content);
	  $preview.attr('src',$elm.attr('src'));
	  $width.prop('value',$elm.innerWidth());
	  $height.prop('value',$elm.innerHeight());
	  $title.prop('value',$elm.attr('title')||'');
	  var proportion=$elm.innerWidth()/$elm.innerHeight();
	  $linked.prop('checked',true);
	  apply=function(){
	    var w=parseInt($width.prop('value'));
	    if (isNaN(w)){
	      w='auto';
	    }
	    var h=parseInt($height.prop('value'));
	    if (isNaN(h)){
	      h='auto';
	    }
	    $elm.css({ width:w, height:h });
	    $elm.attr('title',$title.prop('value'));
	  };
	  var applyTimer;
	  var delayedApply=function(){
	    clearTimeout(applyTimer);
	    applyTimer=setTimeout(apply,50);
	  }
	  var widthChanged=function(){
	    if ($linked.prop('checked')){
	      var w=parseInt($(this).prop('value'));
	      if (!isNaN(w)){
		$height.prop('value',w/proportion);
	      };
	    };
	    delayedApply();
	  };
	  var heightChanged=function(){
	    if ($linked.prop('checked')){
	      var h=parseInt($(this).prop('value'));
	      if (!isNaN(h)){
		$width.prop('value',h*proportion);
	      };
	    };
	    delayedApply();
	  };
	  $width.keyup(widthChanged);
	  $height.keyup(heightChanged);
	  $width.change(widthChanged);
	  $height.change(heightChanged);
	  $title.keyup(delayedApply());
	  $title.change(delayedApply());
	  $linked.change(function(){
	    if ($(this).prop('checked')){
	      proportion=
		parseInt($width.prop('value'))/
		parseInt($height.prop('value'));
	    }
	  });
	  $changeImage.button().click(function(){
	    kc.uploadFile($,'Choose Image')
	      .then(function(url,originalFileName){
		if (!url){
		  editor.focus();
		  return;
		}
		$preview.attr('src',url);
		$elm.attr('src',url);
		$elm.attr('data-mce-src',url);
		if (!$elm.get().complete){
		  $elm.load(delayedApply);
		}
	      });
	    return false;
	  });
	})
	.always(function(result){
	  $('.tinymce_image2_dialog').removeClass('kc-busy-cursor');
	});
    };
    if (imgElm){
      if (!imgElm.complete){
	$(imgElm).load(function(){
	  editImage($(imgElm));
	});
      }
      else{
	editImage($(imgElm));
      }
    }
    else{
      kc.uploadFile($,'Choose Image')
	.then(function(url,originalFileName){
	  if (!url){
	    editor.focus();
	    return;
	  }
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
	    if (!imgElm.complete){
	      $(imgElm).load(function(){
		editImage($(imgElm));
	      });
	    }
	    else{
	      editImage($(imgElm));
	    }
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
