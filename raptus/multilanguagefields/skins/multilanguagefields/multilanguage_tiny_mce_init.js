/*
 * Helper script setting the text format to text/html and hiding it
 * for multilanguage TinyMCE fields
 */
if (typeof(kukit) != "undefined") {
  jq(document).ready(function() {
    jq('.languageMultiplier textarea.mce_editable').each(function() {
      jq(this).closest('.formPanel').find('.fieldTextFormat').hide().find('select').val('text/html');
    });
  });
}