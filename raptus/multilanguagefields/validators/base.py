class MultilanguageValidatorMixin:
    def __call__(self, value, *args, **kwargs):
        field = kwargs['field']
        instance = kwargs['instance']
        form = kwargs.get('REQUEST', instance.REQUEST).form
        languages = field.getAvailableLanguages(instance)
        for lang in languages:
            result = self.base_class.__call__(self, form.get('%s___%s___' % (field.getName(), lang['name'])), *args, **kwargs)
            if isinstance(result, basestring):
                return result
