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

tinymce.PluginManager.add('image', function(editor) {
	function getImageSize(url, callback) {
		var img = document.createElement('img');

		function done(width, height) {
			if (img.parentNode) {
				img.parentNode.removeChild(img);
			}

			callback({width: width, height: height});
		}

		img.onload = function() {
			done(Math.max(img.width, img.clientWidth), Math.max(img.height, img.clientHeight));
		};

		img.onerror = function() {
			done();
		};

		var style = img.style;
		style.visibility = 'hidden';
		style.position = 'fixed';
		style.bottom = style.left = 0;
		style.width = style.height = 'auto';

		document.body.appendChild(img);
		img.src = url;
	}

	function showDialog() {
		var win, data = {}, dom = editor.dom, imgElm, figureElm;
		var width, height, imageDimensions = editor.settings.image_dimensions !== false;

		function recalcSize() {
			var widthCtrl, heightCtrl, newWidth, newHeight;

			widthCtrl = win.find('#width')[0];
			heightCtrl = win.find('#height')[0];

			if (!widthCtrl || !heightCtrl) {
				return;
			}

			newWidth = widthCtrl.value();
			newHeight = heightCtrl.value();

			if (win.find('#constrain')[0].checked() && width && height && newWidth && newHeight) {
				if (width != newWidth) {
					newHeight = Math.round((newWidth / width) * newHeight);

					if (!isNaN(newHeight)) {
						heightCtrl.value(newHeight);
					}
				} else {
					newWidth = Math.round((newHeight / height) * newWidth);

					if (!isNaN(newWidth)) {
						widthCtrl.value(newWidth);
					}
				}
			}

			width = newWidth;
			height = newHeight;
		}

		function onSubmitForm() {
			var figureElm, oldImg;

			function waitLoad(imgElm) {
				function selectImage() {
					imgElm.onload = imgElm.onerror = null;

					if (editor.selection) {
						editor.selection.select(imgElm);
						editor.nodeChanged();
					}
				}

				imgElm.onload = function() {
					if (!data.width && !data.height && imageDimensions) {
						dom.setAttribs(imgElm, {
							width: imgElm.clientWidth,
							height: imgElm.clientHeight
						});
					}

					selectImage();
				};

				imgElm.onerror = selectImage;
			}

			recalcSize();

			data = tinymce.extend(data, win.toJSON());

			if (!data.alt) {
				data.alt = '';
			}

			if (!data.title) {
				data.title = '';
			}

			if (data.width === '') {
				data.width = null;
			}

			if (data.height === '') {
				data.height = null;
			}

			if (!data.style) {
				data.style = null;
			}

			// Setup new data excluding style properties
			/*eslint dot-notation: 0*/
			data = {
				src: data.src,
				alt: data.alt,
				title: data.title,
				width: data.width,
				height: data.height,
				style: data.style,
				caption: data.caption,
				"class": data["class"]
			};

			editor.undoManager.transact(function() {
				if (!data.src) {
					if (imgElm) {
						dom.remove(imgElm);
						editor.focus();
						editor.nodeChanged();
					}

					return;
				}

				if (data.title === "") {
					data.title = null;
				}

				if (!imgElm) {
					data.id = '__mcenew';
					editor.focus();
					editor.selection.setContent(dom.createHTML('img', data));
					imgElm = dom.get('__mcenew');
					dom.setAttrib(imgElm, 'id', null);
				} else {
					dom.setAttribs(imgElm, data);
				}

				editor.editorUpload.uploadImagesAuto();

				if (data.caption === false) {
					if (dom.is(imgElm.parentNode, 'figure.image')) {
						figureElm = imgElm.parentNode;
						dom.insertAfter(imgElm, figureElm);
						dom.remove(figureElm);
					}
				}

				function isTextBlock(node) {
					return editor.schema.getTextBlockElements()[node.nodeName];
				}

				if (data.caption === true) {
					if (!dom.is(imgElm.parentNode, 'figure.image')) {
						oldImg = imgElm;
						imgElm = imgElm.cloneNode(true);
						figureElm = dom.create('figure', {'class': 'image'});
						figureElm.appendChild(imgElm);
						figureElm.appendChild(dom.create('figcaption', {contentEditable: true}, 'Caption'));
						figureElm.contentEditable = false;

						var textBlock = dom.getParent(oldImg, isTextBlock);
						if (textBlock) {
							dom.split(textBlock, oldImg, figureElm);
						} else {
							dom.replace(figureElm, oldImg);
						}

						editor.selection.select(figureElm);
					}

					return;
				}

				waitLoad(imgElm);
			});
		}

		function srcChange(e) {
			var srcURL, prependURL, absoluteURLPattern, meta = e.meta || {};

			tinymce.each(meta, function(value, key) {
				win.find('#' + key).value(value);
			});

			if (!meta.width && !meta.height) {
				srcURL = editor.convertURL(this.value(), 'src');

				// Pattern test the src url and make sure we haven't already prepended the url
				prependURL = editor.settings.image_prepend_url;
				absoluteURLPattern = new RegExp('^(?:[a-z]+:)?//', 'i');
				if (prependURL && !absoluteURLPattern.test(srcURL) && srcURL.substring(0, prependURL.length) !== prependURL) {
					srcURL = prependURL + srcURL;
				}

				this.value(srcURL);

				getImageSize(editor.documentBaseURI.toAbsolute(this.value()), function(data) {
					if (data.width && data.height && imageDimensions) {
						width = data.width;
						height = data.height;

						win.find('#width').value(width);
						win.find('#height').value(height);
					}
				});
			}
		}

		imgElm = editor.selection.getNode();
		figureElm = dom.getParent(imgElm, 'figure.image');
		if (figureElm) {
			imgElm = dom.select('img', figureElm)[0];
		}

		if (imgElm && (imgElm.nodeName != 'IMG' || imgElm.getAttribute('data-mce-object') || imgElm.getAttribute('data-mce-placeholder'))) {
			imgElm = null;
		}

		if (imgElm) {
			width = dom.getAttrib(imgElm, 'width');
			height = dom.getAttrib(imgElm, 'height');

			data = {
				src: dom.getAttrib(imgElm, 'src'),
				alt: dom.getAttrib(imgElm, 'alt'),
				title: dom.getAttrib(imgElm, 'title'),
				"class": dom.getAttrib(imgElm, 'class'),
				width: width,
				height: height,
				caption: !!figureElm
			};
		}

		// General settings shared between simple and advanced dialogs
		var jquery_=$;
		var generalFormItems = [{
			type: 'container',
			label: 'Source',
			layout: 'flex',
			direction: 'row',
			align: 'center',
			spacing: 5,
			items: [
				{
					name: 'src',
					type: 'filepicker',
					filetype: 'image',
					label: 'Source',
					autofocus: true,
					onchange: srcChange
				},
				{
					type: 'label',
					text: ' or '
				},
				{
					type: 'button', 
					text: 'Upload...',
					onclick: function(){
						kc.uploadFile(jquery_)
					    .then(function(url,originalFileName){
								win.find('#src').value(url);
							})
							.$dialog.closest('.ui-dialog').css('z-index',65539)
							.closest('.ui-widget-overlay').css('z-index',65538);
					}
				}
			]
		}];

		if (editor.settings.image_description !== false) {
			generalFormItems.push({name: 'alt', type: 'textbox', label: 'Image description'});
		}

		if (editor.settings.image_title) {
			generalFormItems.push({name: 'title', type: 'textbox', label: 'Image Title'});
		}

		if (imageDimensions) {
			generalFormItems.push({
				type: 'container',
				label: 'Dimensions',
				layout: 'flex',
				direction: 'row',
				align: 'center',
				spacing: 5,
				items: [
					{name: 'width', type: 'textbox', maxLength: 5, size: 3, onchange: recalcSize, ariaLabel: 'Width'},
					{type: 'label', text: 'x'},
					{name: 'height', type: 'textbox', maxLength: 5, size: 3, onchange: recalcSize, ariaLabel: 'Height'},
					{name: 'constrain', type: 'checkbox', checked: true, text: 'Constrain proportions'}
				]
			});
		}

		if (editor.settings.image_caption && tinymce.Env.ceFalse) {
			generalFormItems.push({name: 'caption', type: 'checkbox', label: 'Caption'});
		}


		if (true) {
			// Simple default dialog
			win = editor.windowManager.open({
				title: 'Insert/edit image',
				data: data,
				body: generalFormItems,
				onSubmit: onSubmitForm
			});
		}
	}

	editor.on('preInit', function() {
		function hasImageClass(node) {
			var className = node.attr('class');
			return className && /\bimage\b/.test(className);
		}

		function toggleContentEditableState(state) {
			return function(nodes) {
				var i = nodes.length, node;

				function toggleContentEditable(node) {
					node.attr('contenteditable', state ? 'true' : null);
				}

				while (i--) {
					node = nodes[i];

					if (hasImageClass(node)) {
						node.attr('contenteditable', state ? 'false' : null);
						tinymce.each(node.getAll('figcaption'), toggleContentEditable);
					}
				}
			};
		}

		editor.parser.addNodeFilter('figure', toggleContentEditableState(true));
		editor.serializer.addNodeFilter('figure', toggleContentEditableState(false));
	});

	editor.addButton('image', {
		icon: 'image',
		tooltip: 'Insert/edit image',
		onclick: showDialog,
		stateSelector: 'img:not([data-mce-object],[data-mce-placeholder]),figure.image'
	});

	editor.addMenuItem('image', {
		icon: 'image',
		text: 'Insert/edit image',
		onclick: showDialog,
		context: 'insert',
		prependToContext: true
	});

	editor.addCommand('mceImage', showDialog);
});
