var translator = {
  translators : new Array(),
  
  Translator : function(field, elm, fieldName, widgetType, lang, id) {
    this.field = field;
    this.elm = elm;
    this.fieldName = fieldName;
    this.widgetType = widgetType;
    this.lang = lang;
    this.id = id;
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
      var dd = dds.get(i);
      var args = dd.id.split('-');
      var t = new translator.Translator(elm, dd, args[1], widgetType, args[2], translator.translators.length);
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
  value = value.split("\n").join("[[N]]");
  while(d = dest.pop()) {
    jq.get(translator.base+'@@getTranslation', 
           {string: value,
            source: this.lang,
            dest: d,
            id: this.id},
           translator.setTranslation);
  }
}

translator.Translator.prototype.setTranslation = function(data) {
  language = jq(this.field).find('#fieldsetlegend-'+this.fieldName+'-'+data.dest+' span').text();
  translation = data.result.responseData.translatedText.split("[[N]]");
  for(var i=0; i<translation.length; i++)
    translation[i] = jq.trim(translation[i]);
  translation = translation.join("\n");
  if(!this.getValue(data.dest) || window.confirm(data.message.replace('{language}', language).replace('{translation}', translator.crop(translation, 150)))) {
    this.setValue(translation, data.dest);
    jq(this.field).find('#fieldsetlegend-'+this.fieldName+'-'+data.dest).click();
  }
  jq(this.elm).find('.spinner').hide();
  jq(this.elm).find('.context').show();
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
      if(elm.find('select:first').val())
        keywords += (keywords ? "\n" : "")+elm.find('select:first').val().join("\n");
      return keywords;
      break;
    case 'rich':
      if (jq('.kupu-editor-iframe', elm).length) {
          return elm.find('.kupu-editor-iframe').contents().find("body").html();
      }
      else if (typeof FCKeditorAPI != 'undefined') {
          if (lang) fieldId = this.fieldName+'___'+lang+'___';
          else fieldId = jq('.fcklinkedField', elm).attr('id');
          return FCKeditorAPI.GetInstance(fieldId).GetXHTML();
      }
      // TODO : other editor implementation
      else if (jq('textarea', elm).length) {
          return elm.find('textarea').val();
      }
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
      for(var i=0; i<value.length; i++)
        if(elm.find('select:first').find('option[value='+value[i]+']').length)
          options.push(value[i]);
        else
          values.push(value[i]);
      elm.find('select:first').val(options);
      elm.find('textarea').val(values.join("\n"));
      break;
    case 'rich':
      if (jq('.kupu-editor-iframe', elm).length) {
          elm.find('.kupu-editor-iframe').contents().find("body").html(value);
      }
      else if (typeof FCKeditorAPI != 'undefined') {
          if (lang) fieldId = this.fieldName+'___'+lang+'___';
          else fieldId = jq('.fcklinkedField', elm).attr('id');          
          FCKeditorAPI.GetInstance(this.fieldName+'___'+lang+'___').SetHTML(value);
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
