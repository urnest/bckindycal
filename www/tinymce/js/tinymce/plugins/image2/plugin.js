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
    var chooseImage;
    var editImage;
    var $dialog;
    var next;
    var cancel;
    chooseImage=function(){
      $dialog.find('div.choose-image-panel').show();
      $dialog.find('div.edit-image-panel').hide();
      $('.edit-image-next-button .ui-button-text').text('Next >>');
      next=function(){
	//REVISIT
      };
      cancel=function(){
	//REVISIT
      };
      $dialog.dialog('open');
    };
    editImage=function(){
      $dialog.find('div.edit-image-panel').show();
      $dialog.find('div.choose-image-panel').hide();
      $('.edit-image-next-button .ui-button-text').text('OK');
      $('.edit-image-cancel-button .ui-button-text').text('<< Back');
      next=function(){
	//REVISIT
      };
      cancel=function(){
	chooseImage();
      };
      $dialog.dialog('open');
    };
    if (!$dialog){
      kc.getFromServer('get_edit_image_panel')
	.then(function(result){
	  $dialog=$(result);
	  $dialog.dialog({
	    autoOpen:false,
	    buttons:[{
	      text:'Cancel',
	      click:function(){
		cancel();
	      },
	      'class':'edit-image-cancel-button'
	    },{
	      text:'Next',
	      click:function(){
		next();
	      },
	      'class':'edit-image-next-button'
	    }]
	  });
	  if (imgElm){
	    editImage();
	  }
	  else{
	    chooseImage();
	  }
	});
    }
    else{
      if (imgElm){
	editImage();
      }
      else{
	chooseImage();
      }
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
