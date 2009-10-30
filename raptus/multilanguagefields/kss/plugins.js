kukit.actionsGlobalRegistry.register("translator", function (oper) {
    oper.evaluateParameters([], {}, 'google translator');
    var i = translator.translators.length;
    translator.init(oper.node);
    if(i > 0)
      translator.translators[i].getTranslator();
});
kukit.commandsGlobalRegistry.registerFromAction('translator', kukit.cr.makeSelectorCommand);

kukit.actionsGlobalRegistry.register("formTabbing", function (oper) {
    oper.evaluateParameters([], {}, 'form tabbing');
    if(oper.node.tagName.toLowerCase() == 'dl')
      jq(oper.node).each(ploneFormTabbing.initializeDL);
    else
      jq(oper.node).each(ploneFormTabbing.initializeForm);
});
kukit.commandsGlobalRegistry.registerFromAction('formTabbing', kukit.cr.makeSelectorCommand);