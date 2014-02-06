/* 2.2011
 * raptus.multilanguagefields
 * 
 * this is a helper script for kss validation. This insert a hidden
 * input field to detect which field was changed as last.
 */

var validation_helper = {
  
  init:function(elm){
    $(elm).find('input, textarea').focus(validation_helper.event);
  },
  
  event:function(obj){
    var form = $('.kssActive form[name="edit_form"]');
    var input = form.find('input[name="multilanguagefield_validation"]');
    if (!input.length)
      form.append('<input type="hidden" name="multilanguagefield_validation" />');
    input = form.find('input[name="multilanguagefield_validation"]');
    input.attr('value', $(obj.target).attr('name'));
  }
}


$('document').ready(function() {
  $('.languageMultiplier').each(function() {
    validation_helper.init(this);
  });
});
