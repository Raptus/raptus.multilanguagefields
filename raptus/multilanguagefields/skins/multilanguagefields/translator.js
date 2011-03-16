var translator = {
  translators : new Array(),
  
  Translator : function(field, elm, fieldName, widgetType, lang, id) {
    this.field = field;
    this.elm = elm;
    this.fieldName = fieldName;
    this.widgetType = widgetType;
    this.lang = lang;
    this.id = id;
    this.dest = new Array();
    this.value = '';
    translator.translators[id] = this;
    if(id == 0)
      this.getTranslator();
    return this;
  },
  
  setTranslator : function(data) {
    data = eval('(' + data + ')');
    translator.get(data.id).setTranslator(data.data);
  },
  
  setTranslation : function(data) {
    data = eval('(' + data + ')');
    translator.get(data.id).setTranslation(data);
  },
  
  get : function(id) {
    return translator.translators[id];
  },
  
  crop : function(string, length) {
    if(string.length <= length)
      return string;
    return string.substring(0, length-3)+'...';
  },
  
  init : function(elm) {
    var widgetType = elm.className.split(' ')[2];
    var dds = jq(elm).find('dd');
    for(var i=0; i<dds.length; i++) {
      var dd = jq(dds.get(i));
      var id = dd.attr('id');
      var fieldname = jq(dd).parents('.field').attr('id');
      fieldname = fieldname.replace('archetypes-fieldname-','');
      var regex = new RegExp('(fieldset-)('+fieldname+')-(.*)','');
      if(!regex.test(id)) continue;
      var args = id.match(regex);
      var t = new translator.Translator(elm, dd, args[2], widgetType, args[3], translator.translators.length);
    }
  }
}

translator.base = jq('base').attr('href');
if(translator.base.substring(-1) != '/')
  translator.base += '/';

translator.Translator.prototype.getTranslator = function() {
  jq.get(translator.base+'@@getTranslator', 
         {fieldName: this.fieldName,
          widgetType: this.widgetType,
          lang: this.lang,
          id: this.id},
         translator.setTranslator);
}

translator.Translator.prototype.setTranslator = function(data) {
  jq(this.elm).append(data);
  jq(this.elm).find('a').click(function() {
    translator.get(this.id.replace('translate', '')).translate();
  });
  if(this.id < translator.translators.length - 1)
    translator.get(this.id+1).getTranslator();
}

translator.Translator.prototype.translate = function() {
  value = this.getValue();
  if(!value) return ;
  
  jq(this.elm).find('.context').hide();
  jq(this.elm).find('.spinner').show();
  
  dest = jq('#language'+this.id).val();
  if(dest == 'all') {
    dest = new Array();
    jq('#language'+this.id+' option').each(function() {
      if(jq(this).val() != 'all')
        dest.push(jq(this).val());
    });
  } else
    dest = new Array(dest);
  this.dest = dest;
  this.value = value.split("\n").join("<break>");
  this.translate_next();
}

translator.Translator.prototype.translate_next = function() {
  if(d = this.dest.pop()) {
    jq.get(translator.base+'@@getTranslation', 
           {string: this.value,
            source: this.lang,
            dest: d,
            id: this.id},
           translator.setTranslation);
  } else {
    jq(this.elm).find('.spinner').hide();
    jq(this.elm).find('.context').show();
  }
}

translator.Translator.prototype.setTranslation = function(data) {
  language = jq(this.field).find('a[href=#fieldsetlegend-'+this.fieldName+'-'+data.dest+'] span').text();
  translation = data.result.responseData.translatedText.split("<break>");
  for(var i=0; i<translation.length; i++)
    translation[i] = jq.trim(translation[i]);
  translation = translation.join("\n");
  if(!this.getValue(data.dest) || window.confirm(data.message.replace('{language}', language).replace('{translation}', translator.crop(translation, 150)))) {
    this.setValue(translation, data.dest);
    jq(this.field).find('#fieldsetlegend-'+this.fieldName+'-'+data.dest).click();
    jq(this.field).find('a[href="#fieldsetlegend-'+this.fieldName+'-'+data.dest+'"]').click();
  }
  this.translate_next();
}

translator.Translator.prototype.getValue = function(lang) {
  if(lang)
    elm = jq(this.field).find('#fieldset-'+this.fieldName+'-'+lang);
  else
    elm = jq(this.elm);
  switch(this.widgetType) {
    case 'string':
      return elm.find('input').val();
      break;
    case 'textarea':
    case 'lines':
      return elm.find('textarea').val();
      break;
    case 'keyword':
      keywords = elm.find('textarea').val();
      if(elm.find('div:not(.translator) select:first').val())
        keywords += (keywords ? "\n" : "")+elm.find('div:not(.translator) select:first').val().join("\n");
      return keywords;
      break;
    case 'rich':
      if (elm.find('.kupu-editor-iframe').size()) {
        return elm.find('.kupu-editor-iframe').contents().find("body").html();
      }
      if (typeof FCKeditorAPI != 'undefined') {
        try {
          if (lang) fieldId = this.fieldName+'___'+lang+'___';
          else fieldId = jq('.fcklinkedField', elm).attr('id');
          return FCKeditorAPI.GetInstance(fieldId).GetXHTML();
        } catch(e) {};
      }
      if (typeof CKEDITOR != 'undefined') {
        try {
          if (!lang) lang = this.lang;
          var fieldId = this.fieldName+'___'+lang+'___';
          return CKEDITOR.instances[fieldId].getData();
        } catch(e) {};
      }
      if (typeof tinyMCE != 'undefined') {
        try {
          if (!lang) lang = this.lang;
          fieldId = this.fieldName+'___'+lang+'___';
          return tinyMCE.get(fieldId).getContent();
        } catch(e) {};
      }
      // TODO : other editor implementation
      else if(jq('textarea', elm).length)
        return elm.find('textarea').val();
      break;
  }
}

translator.Translator.prototype.setValue = function(value, lang) {
  elm = jq(this.field).find('#fieldset-'+this.fieldName+'-'+lang);
  switch(this.widgetType) {
    case 'string':
      elm.find('input').val(value);
      break;
    case 'textarea':
    case 'lines':
      elm.find('textarea').val(value);
      break;
    case 'keyword':
      value = value.split("\n");
      values = new Array();
      options = new Array();
      for(var i = 0; i < value.length; i++) {
        option = false;
        elm.find('div:not(.translator) select:first').find('option').each(function() {
          if($(this).val() == value[i]) {
            options.push(value[i]);
            option = true;
          }
        });
        if(!option)
          values.push(value[i]);
      }
      elm.find('div:not(.translator) select:first').val(options);
      elm.find('textarea').val(values.join("\n"));
      break;
    case 'rich':
      if (elm.find('.kupu-editor-iframe').size()) {
        elm.find('.kupu-editor-iframe').contents().find("body").html(value);
        return;
      }
      if (typeof FCKeditorAPI != 'undefined') {
        try {
          if (lang) fieldId = this.fieldName+'___'+lang+'___';
          else fieldId = jq('.fcklinkedField', elm).attr('id');
          FCKeditorAPI.GetInstance(this.fieldName+'___'+lang+'___').SetHTML(value);
          return;
        } catch(e) {};
      }
      if (typeof CKEDITOR != 'undefined') {
        try {
          if (!lang) lang = this.lang;
          var fieldId = this.fieldName+'___'+lang+'___';
          CKEDITOR.instances[fieldId].setData(value);
          return;
        } catch(e) {};
      }
      if (typeof tinyMCE != 'undefined') {
        try {
          if (!lang) lang = this.lang;
          fieldId = this.fieldName+'___'+lang+'___';
          return tinyMCE.get(fieldId).setContent(value);
        } catch(e) {};
      }
      // TODO : other editor implementation
      else if (jq('textarea', elm).length) {
        elm.find('textarea').val(value);
      }
      break;
  }
}

jq('document').ready(function() {
  jq('.hasTranslator').each(function() {
    translator.init(this);
  });
});
