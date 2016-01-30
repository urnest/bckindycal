(function( kc, undefined ) {
  kc.clone=function(x){
    if (x===null){
      return x;
    }
    else if (typeof(x) == 'object' && x.constructor === Array){
      var result=[];
      kc.each(x, function(i){
	result.push(kc.clone(x[i]));
      });
      return result;
    }
    else if (typeof(x)=='object'){
      var result;
      if (typeof(x.ebClone)=='function'){
	result=x.ebClone();
      }
      else {
	result={}
	for(k in x){
	  result[k]=kc.clone(x[k]);
	}
      }
      return result;
    }
    else return x;
  };

  kc.defined=function(x){
    return !(x==undefined);
  }

  // iterate over x:
  // - where x is array, call f(i, x[i]) for i in 0..x.length
  // - where x is object, call f(k, x[k]) for k in x.keys
  kc.each=function(x, f){
    var xt=typeof(x);
    var isArray;
    if (xt=='object'){
      isArray = (Array === x.constructor);
      if (isArray) {
	for(var i=0;i!=x.length;++i){
	  f(i, x[i]);
	}
      }
      else{
	for(var k in x){
	  f(k, x[k]);
	}
      }
    }
  };
  kc.find=function(x, predicate){
    var result=[];
    kc.each(x, function(key, value){
      if (predicate(value)){
	result.push(key);
      }
    });
    return result;
  };
  kc.formatDate=function(date){
    return kc.join('/',[date.day,date.month,date.year]);
  };

  // Get background of (first of) $item, as a css dictionary
  kc.getBackground=(function(){
    var result=function($item) {
      // jquery is bizarre here, $item.parents() is in "upwards" order,
      // but $item.parents().andSelf() is in "downward" order. There
      // is no selfAnd().
      var $items=$item.parents().andSelf();
      var result=getBackground_($items);
      return result;
    };
    // get the background style of the first item with non-transparent
    // background
    // pre: $items.length > 0
    function getBackground_($items) {
      if ($items.length == 1 || bgIsOpaque($items.last())) {
	return {
	  'background-color' : colourAsHex($items.last().css('background-color')||'transparent'),
          'background-image' : $items.last().css('background-image')||'none',
	  'background-position' : $items.last().css('background-position')||'left top',
	  'background-repeat' : $items.last().css('background-repeat')||'repeat'
	};
      }
      return getBackground_($items.slice(0, -1));
    }
    function bgIsOpaque($x) {
      var b=$x.css('background-color');
      return (b != 'transparent' && !zeroAlphaColour(b)) ||
	$x.css('background-image') != 'none';
    }
    var alphaRE=
      /rgba[(][0-9][0-9]*[ ]*,[ ]*[0-9][0-9]*[ ]*,[ ]*[0-9][0-9]*[ ]*,[ ]*([0-9][0-9]*)[ ]*[)]/;
    function zeroAlphaColour(c){
      var m=alphaRE.exec(''+c);
      return m && Number(m[1])==0;
    }
    // convert rgb(x,y,z) to #xyz
    // leave #xyz as #xyz
    function colourAsHex(c){
      if (c.search(/rgb/)==0){
	var r=c.split(',');
	r[0]=r[0].split('(')[1]
	r[2]=r[2].split(')')[0]
	
	c='#'+
	  hexChar[parseInt(r[0]/16)]+hexChar[r[0]%16]+
	  hexChar[parseInt(r[1]/16)]+hexChar[r[1]%16]+
	  hexChar[parseInt(r[2]/16)]+hexChar[r[2]%16];
      }
      return c;
    }
    
    var hexChar=[
      '0',
      '1',
      '2',
      '3',
      '4',
      '5',
      '6',
      '7',
      '8',
      '9',
      'A',
      'B',
      'C',
      'D',
      'E',
      'F'
    ];
    return result;
  })();

  kc.inContext=function(e, context){
    var em;
    if (typeof(e)=='object' && 
	kc.defined(e.name) &&
	kc.defined(e.message)){
      em=e.name+': '+e.message;
    }
    else{
      em=''+e;
    }
    // replace newlines with " " because IE won't let you scroll error
    // window or select the text, so we lose the stuff off the bottom
    // of the window
    return ('failed to '+context+' because '+em).replace("\n", " ");
  };
  kc.keys=function(x){
    return kc.map(x,function(k,v){return k;});
  }
  kc.map=function(x, f){
    var result=[];
    kc.each(x, function(k, v){
      result.push(f(k, v));
    });
    return result;
  };
  kc.getFromServer=function(url,data){
    var result={
      then_: function(){},
      error_:function(e){
	alert(e);
      },
      always_:function(){
      }
    };
    result.then=function(then){
      result.then_=then;
      return result;
    }
    result.or=function(error){
      result.error_=error;
      return result;
    }
    result.always=function(always){
      result.always_=always;
      return result;
    }
    $.ajax({ 
      type: 'GET',
      url: url,
      data: data,
      dataType: 'text',
      cache:false,
      success: function(responseData_, status){
	var responseData;
	try{
	  responseData=kc.json.decode(responseData_);
	}
	catch(e){
	  result.error_(kc.inContext(''+e, 'get url '+url));
	  result.always_();
	  return;
	}
        if (typeof(responseData.error) != 'undefined' && 
	    responseData.error != '') {
	  result.error_(kc.inContext(''+responseData.error, 'get url '+url));
        }
        else {
          if (window.console&&console.log&&responseData.msg) {
	    console.log(''+responseData.msg);
	  };
	  result.then_(responseData.result);
        }
	result.always_();
      },
      error: function(jqXHR, status, e){
	result.error_(kc.inContext(''+e, 'get url '+url));
	result.always_();
      }
    });
    return result;
  };

  kc.join=function(sep, array){
    if (array.length==0){
      return '';
    }
    var result=''+array[0];
    for(var i=1; i != array.length; ++i){
      result=result+sep+array[i];
    }
    return result;
  }

  kc.json={};

  // encode o, using specified prefix as base indentation for all but first line
  // of encoding result (first line is not indented)
  kc.json.encode = function(o, prefix) {
    //if (typeof (JSON) == 'object' && JSON.stringify)
    //    return JSON.stringify(o);
    prefix=prefix||'';
    
    var type = typeof (o);
    
    if (o === null)
      return "null";
    
    if (type == "undefined")
      return "undefined";
    
    if (type == "number" || type == "boolean")
      return o;
    
    if (type == "string")
      return quoteString(o);
    
    if (type == 'object') {
      if (typeof o.toJSON == "function")
        return o.toJSON(prefix);
      
      if (o.constructor === Array) {
        var ret = [];
	var skipped=0;
        for ( var i = 0; i < o.length; i++){
	  if (typeof(o[i])=='function'){
	    ++skipped;
	  }
	  else if (typeof(o[i])=='undefined'){
	    ret.push("\n"+prefix+"\t"+kc.json.encode(null, prefix+"\t"));
	  }
	  else {
            ret.push("\n"+prefix+"\t"+kc.json.encode(o[i], prefix+"\t"));
	  }
	}
	if (skipped && skipped != o.length){
	  throw new String(
	    'kc.json.encode array has mixture of functions and data');
	}
        return "[" + ret.join(",") + "\n"+prefix+"]";
      }
      
      var pairs = [];
      for ( var k in o) {
        var name;
        var type = typeof k;
	
        if (type == "number")
          name = '"' + k + '"';
        else if (type == "string")
          name = quoteString(k);
        else
          continue; // skip non-string or number keys
	
        if (typeof o[k] == "function")
          continue; // skip pairs where the value is a function.
	if (!kc.defined(o[k])){
	  continue; // skip pairs where the value is undefined
	}
        var val = kc.json.encode(o[k], prefix+"\t");
	
        pairs.push("\n"+prefix+"\t"+name + ": " + val);
      }
      
      return "{" + pairs.join(",") + "\n"+prefix+"}";
    }
  };
  
  //
  // Decode JSON encoded string.
  //
  kc.json.decode = function(src) {
    try{
      return eval('('+src+')');
    }
    catch(e){
      var i=new Iterator(src);
      return i.parse();
    }
  }
 
  var quoteString=function(string) {
        if (string.match(_escapeable)) {
            return '"' + string.replace(_escapeable, function(a) {
                var c = _meta[a];
                if (typeof c === 'string')
                    return c;
                c = a.charCodeAt();
                return '\\u00' + Math.floor(c / 16).toString(16)
                        + (c % 16).toString(16);
            }) + '"';
        }
        return '"' + string + '"';
  };
 
  var _escapeable= /["\\\x00-\x1f\x7f-\x9f]/g;

  var _meta= {
        '\b': '\\b',
        '\t': '\\t',
        '\n': '\\n',
        '\f': '\\f',
        '\r': '\\r',
        '"': '\\"',
        '\\': '\\\\'
  };

  var Iterator=function(s){
    this.val=s;
    this.line=1;
    this.char=1;
  }
  Iterator.prototype.lineAndChar=function(){
    return 'line ' + this.line + ', char ' + this.char;
  }
  // Advance past s, which is assumed to exist at start
  // of this.val.
  Iterator.prototype.advance=function(s){
    this.val=this.val.slice(s.length);
    var m=0;
    var i=0;
    while((m=s.indexOf('\n',i))!=-1){
      ++this.line;
      this.char=0;
      i=m+1;
    }
    this.char+=s.length-i;
  }
  // Advance n chars assuming none of those are newlines
  Iterator.prototype.advanceInLine=function(n){
    this.val=this.val.slice(n);
    this.char+=n;
  }
  // Parse to first occurrance of re.
  // - if re not found, advance to end if allowEnd is true; otherwise
  //   raise exception
  // - return up to resulting point (as string)
  Iterator.prototype.parseTo=function(re, allowEnd){
    var m=this.val.search(re);
    var result='';
    if (m != -1){
      result=this.val.substr(0,m);
      this.advance(result);
    }
    else {
      if (allowEnd){
	result=this.val;
	this.advance(result);
      }
      else{
	throw re.pattern+' not found aftr '+this.lineAndChar();
      }
    }
    return result;
  }
  // Skip leading whitespace.
  Iterator.prototype.skipWhite=function(){
    this.parseTo(whiteRE, true);
    return this;
  }
  // Parse literal l which is assumed to exist at start of this.val.
  // - does not skip subsequent whitespace
  // - assumes l contains no newlines
  Iterator.prototype.parseLiteral=function(l){
    if (this.val.substr(0,l.length)!=l){
      throw l+' not found at '+this.lineAndChar();
    }
    this.advanceInLine(l.length);
    return this;
  }
  // Parse number assumed to exist at start of this.val.
  // - returns number, and advances past it and any subsequent whitespace
  Iterator.prototype.parseNumber=function(){
    var n=this.parseTo(numberRE, true);
    if (n==''){
      throw 'invalid number at ' + this.lineAndChar()
    }
    this.skipWhite();
    return Number(n);
  }
  // Parse string assumed to exist at start of this.val.
  // - returns string, and advances past it and any subsequent whitespace
  //pre: iterator positioned at opening '"'
  Iterator.prototype.parseString=function(){
    this.parseLiteral('"');
    var result=this.parseTo(parseStringRE,false);
    while(this.val.length && this.val.charAt(0) == "\\"){
      switch(this.val.charAt(0)){
      case 'b':
	result+='\b';
	this.advanceInLine(2);
	break;
      case 't':
	result+='\t';
	this.advanceInLine(2);
	break;
      case 'n':
	result+='\n';
	this.advanceInLine(2);
	break;
      case 'f':
	result+='\f';
	this.advanceInLine(2);
	break;
      case 'r':
	result+='\r';
	this.advanceInLine(2);
	break;
      case '"':
	result+='"';
	this.advanceInLine(2);
	break;
      case 'u':
	if (this.val.length < 5){
	  result+=this.val;
	  this.advance(this.val);
	}
	else{
	  result+=String.fromCharCode(parseInt(this.val.substr(2,4), 16));
	  this.advanceInLine(6);
	}
	break;
      default:
	result+=this.val.charAt(1);
	this.advanceInLine(2);
	break;
      }
      result=result+this.parseTo(parseStringRE,false);
    }
    if (this.val.charAt(0) != '"'){
      throw 'unterminated string at '+this.lineAndChar();
    }
    this.parseLiteral('"');
    this.skipWhite();
    return result;
  }
  // Parse entity assumed to exist at start of this.val
  // - returns parsed entity, and advances past it and any subsequent whitepspace
  //pre: whitespace has been skipped
  Iterator.prototype.parse=function(){
    switch(this.val.charAt(0)){
    case '"':
      return this.parseString();
    case '[':
      return this.parseArray();
    case '{':
      return this.parseObject();
    case 'n':
      this.parseLiteral('null');
      this.skipWhite();
      return null;
    case 't':
      this.parseLiteral('true');
      this.skipWhite();
      return true;
    case 'f':
      this.parseLiteral('false');
      this.skipWhite();
      return false;
    default:
      return this.parseNumber();
    }
  }
  // Parse array assumed to exist at start of this.val.
  // - returns array, and advances past it and any subsequent whitespace
  //pre: iterator positioned at opening '['
  Iterator.prototype.parseArray=function(){
    this.parseLiteral('[');
    this.skipWhite();
    var result=[],x;
    while(this.val.length && this.val.charAt(0) != ']'){
      result.push(this.parse());
      if (this.val.charAt(0)==','){
	this.parseLiteral(',');
	this.skipWhite();
      }
    }
    if (this.val.charAt(0) != ']'){
      throw 'unterminated array at '+this.lineAndChar();
    }
    this.parseLiteral(']');
    this.skipWhite();
    return result;
  }
  // Parse object assumed to exist at start of this.val.
  // - returns object, and advances past it and any subsequent whitespace
  // pre: iterator positioned at opening '{'
  Iterator.prototype.parseObject=function(){
    this.parseLiteral('{');
    this.skipWhite();
    var result={};
    while(this.val.length && this.val.charAt(0) != '}'){
      var k=this.parse();
      if (typeof(k)!='string' && typeof(k)!='number'){
	throw 'invalid key type '+typeof(k)+' at '+this.lineAndChar();
      }
      if (this.val.charAt(0) != ':'){
	throw 'missing ":" at '+this.lineAndChar();
      }
      this.parseLiteral(':');
      this.skipWhite();
      var val=this.parse();
      result[k] = val;
      if (this.val.charAt(0)==','){
	this.parseLiteral(',');
	this.skipWhite();
      }
    }
    if (this.val.charAt(0) != '}'){
      throw 'missing end } at ' + this.lineAndChar();
    }
    this.parseLiteral('}');
    this.skipWhite();
    return result;
  }

  var lineRE=/[\n]/m;
  var whiteRE = /[^ \t\r\n]/m;
  var numberRE=/[^+\-0-9.eE]/;
  var parseStringRE=/[\\"]/;

  var $load_image;

  kc.loadImage=function(){
    var result={
      then_: function(){},
      error_:function(e){
	alert(kc.inContext(e, 'upload image'));
      }
    };
    result.then=function(then){
      result.then_=then;
      return result;
    }
    result.or=function(error){
      result.error_=error;
      return result;
    }
    if (!$load_image) {
      $load_image = $('.eb_load_image_dialog').removeClass('.eb_template')
      $load_image.dialog({
	autoOpen : false,
	modal: true,
	width: 'auto',
	height: 'auto',
	buttons : {
          "Ok" : function() {
	    var $dlg = $(this); // for use below where this is something else
            //starting setting some animation when the ajax starts and completes
            false||$("#loading") //REVISIT
              .ajaxStart(function(){
		$(this).show();
              })
              .ajaxComplete(function(){
		$(this).hide();
              });
            
            $.ajaxFileUpload({
              url:'loadImage',
              secureuri:false,
              fileElementId:'load_image_filename',
              dataType: 'text',
              success: function (d, status)
              {
		var data=kc.json.decode(d);
                if(data.error) {
                  result.error_(data.error);
                }
		else {
                  result.then_(data.id);
                  $dlg.dialog('close');
                }
              },
              error: function (data, status, e)
              {
                result.then_(e);
              }
            });
            
            return false;
          },
          "Cancel" : function() {
            $(this).dialog('close');
            return false;
          }
	}
      });
    }
    $load_image.dialog('open');

    return result;
  };

  kc.postToServer=function(url,data,sync){
    var result={
      then_: function(){},
      error_:function(e){
	alert(e);
      },
      always_:function(){
      }
    };
    result.then=function(then){
      result.then_=then;
      return result;
    };
    result.or=function(error){
      result.error_=error;
      return result;
    };
    result.always=function(always){
      result.always_=always;
      return result;
    }
    $.ajax({ 
      type: 'POST',
      url: url,
      data: data,
      dataType: 'text',
      async: !sync,
      success: function(responseData_, status){
	var responseData;
	try{
	  responseData=kc.json.decode(responseData_);
	}
	catch(e){
	  result.error_(''+e);
	  result.always_();
	  return;
	}
        if (typeof(responseData.error) != 'undefined' && 
	    responseData.error != '') {
	  result.error_(''+responseData.error);
        }
        else {
          if (window.console&&console.log&&responseData.msg) {
	    console.log(''+responseData.msg);
	  };
	  result.then_(responseData.result);
        }
	result.always_();
      },
      error: function(jqXHR, status, e){
	result.error_(kc.inContext(''+e, 'post data to '+url));
	result.always_();
      }
    });
    return result;
  };
  kc.rendering=function($x){
    var $overlay=$('<div class="kc-busy-cursor">&nbsp;</div>').css({
      position:'absolute',
      left:0,
      top:0,
      width:'100%',
      height:'100%'})
      .css(kc.getBackground($x));
    $x.append($overlay);
    $x.addClass('kc-rendering');
    return {
      done:function(){
	$overlay.remove();
	$x.removeClass('kc-rendering');
      }
    };
  };
  kc.selectYourGroup=function(title,options,$from){
    var animDuration=200;
    var $dialogContent=$('<div>');
    var $dialog;
    var $option_t=$from.clone();
    var result={
      then_:function(groupsToShow){
      }
    };
    result.then=function(f){
      result.then_=f;
    };
    kc.each(options,function(i,option){
      var $o=$option_t.clone();
      $o.text(option.text);
      $dialogContent.append($('<div class="select-your-group-button">').html($o));
      $o.click(function(){
	$dialog.addClass('kc-invisible');
	$dialog.effect('transfer',{
	  to:$from,
	  className:'kc-transfer-effect'
	},animDuration);
	setTimeout(function(){
	  $dialog.removeClass('kc-invisible');
	  $dialogContent.dialog('close');
	  $dialog.remove();
	  result.then_(option.groups);
	},animDuration);
	return false;
      });
    });
    $dialogContent.dialog({
      autoOpen:false,
      title: title,
      closeOnEscape:false,
      dialogClass:'kc-no-close-dialog'
    });
    $dialog=$dialogContent.parent('.ui-dialog');
    $dialog.addClass('kc-invisible');
    $dialog.addClass('kc-in-front-of-navbar');
    $dialogContent.dialog('open');
    $from.effect('transfer',{
      to:$dialog,
      className:'kc-transfer-effect'
    },animDuration);
    setTimeout(function(){ $dialog.removeClass('kc-invisible');},animDuration);
    return result;
  };
  kc.showError=function(e){
    alert(''+e);
  };
  kc.uploadFile=function(jquery_){
    var result={
      then_: function(url){},
      error_:function(e){
	alert(e);
      },
      always_:function(){
      }
    };
    result.then=function(then){
      result.then_=then;
      return result;
    };
    result.or=function(error){
      result.error_=error;
      return result;
    };
    result.always=function(always){
      result.always_=always;
      return result;
    }
    var $=jquery_||$;
    var $dialog=$('<form action="" method="POST" enctype="multipart/form-data"><p>File: <input id="filename" type="file" name="filename"></p></form>');
    $dialog.dialog({
      modal: true,
      buttons:{
	'OK': function(){
          $.ajaxFileUpload({
            url:'uploaded_file',
            secureuri:false,
            fileElementId:'filename',
            dataType: 'text',
            success: function (d, status)
            {
	      var data=kc.json.decode(d);
              if(data.error) {
                result.error_(data.error);
              }
	      else {
                result.then_('uploaded_file?id='+data.result.id);
                $dialog.dialog('close');
              }
            },
            error: function (data, status, e)
            {
              result.error_(e);
            }
          });
	},
	'Cancel':function(){
	  $dialog.dialog('close');
	  result.then_();
	}
      }
    });
    $dialog.dialog('open');
    result.$dialog=$dialog;
    return result;
  };
}( window.kc = window.kc || {} ));
