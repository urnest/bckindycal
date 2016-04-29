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

tinymce.PluginManager.add('upload_doc', function(editor) {
  var $d;
  var selection, dom, selectedElm, anchorElm, onlyText, initialText;
  function insertLink(data) {
    var linkAttrs = {
      href: data.href,
      title: data.title
    };
    
    if (anchorElm) {
      editor.focus();
      
      if (onlyText && data.text != initialText) {
	if ("innerText" in anchorElm) {
	  anchorElm.innerText = data.text;
	} else {
	  anchorElm.textContent = data.text;
	}
      }
      
      dom.setAttribs(anchorElm, linkAttrs);
      
      selection.select(anchorElm);
      editor.undoManager.add();
    } else {
      if (onlyText) {
	editor.insertContent(dom.createHTML('a', linkAttrs, dom.encode(data.text)));
      } else {
	editor.execCommand('mceInsertLink', false, linkAttrs);
      }
    }
  }
  function isOnlyTextSelected() {
    var html = selection.getContent();
    
    // Partial html and not a fully selected anchor element
    if (/</.test(html) && (!/^<a [^>]+>[^<]+<\/a>$/.test(html) || html.indexOf('href=') == -1)) {
      return false;
    }
    return true;
  }
  function uploadDoc(){
    selection = editor.selection;
    dom = editor.dom;
    selectedElm = selection.getNode();
    anchorElm = dom.getParent(selectedElm, 'a[href]');
    onlyText = isOnlyTextSelected();
    initialText = anchorElm ? 
      (anchorElm.innerText || anchorElm.textContent) : 
      selection.getContent({format: 'text'});
    kc.uploadFile()
      .then(function(url,originalFileName){
	if (url){
	  insertLink({
	    href: url,
	    text: originalFileName,
	    title: originalFileName
	  });
	}
      });
  };
  
  editor.addCommand('mceUploadDoc', uploadDoc);
  
  editor.addMenuItem('upload_doc', {
    text: 'Upload Document',
    onclick: uploadDoc,
    stateSelector: 'a[href]',
    context: 'insert',
    prependToContext: true
  });
});
