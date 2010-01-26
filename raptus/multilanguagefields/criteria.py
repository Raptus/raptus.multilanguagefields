from Products.ATContentTypes import criteria

SORT_INDICES = ('MultilanguageDateIndex', 
                'MultilanguageDateRangeIndex', 
                'MultilanguageFieldIndex', 
                'MultilanguageKeywordIndex')

DATE_INDICES = ('MultilanguageDateIndex', 
                'MultilanguageDateRangeIndex', 
                'MultilanguageFieldIndex')

LIST_INDICES = ('MultilanguageFieldIndex', 
                'MultilanguageKeywordIndex')

TEXT_INDICES = ('MultilanguageZCTextIndex',)

STRING_INDICES = LIST_INDICES + TEXT_INDICES

REFERENCE_INDICES = ('MultilanguageFieldIndex', 
                     'MultilanguageKeywordIndex')
FIELD_INDICES = ('MultilanguageFieldIndex',)

RELEVANT_INDICES=list(DATE_INDICES + criteria.DATE_INDICES)
RELEVANT_INDICES.remove('MultilanguageDateRangeIndex')
RELEVANT_INDICES.remove('DateRangeIndex')
RELEVANT_INDICES = tuple(RELEVANT_INDICES)

criteria.registerCriterion(criteria.ATSortCriterion, SORT_INDICES + criteria.SORT_INDICES)
criteria.registerCriterion(criteria.ATSimpleStringCriterion, STRING_INDICES + criteria.STRING_INDICES)
criteria.registerCriterion(criteria.ATSimpleIntCriterion, LIST_INDICES + criteria.LIST_INDICES)
criteria.registerCriterion(criteria.ATSelectionCriterion, LIST_INDICES + criteria.LIST_INDICES)
criteria.registerCriterion(criteria.ATListCriterion, LIST_INDICES + criteria.LIST_INDICES)
criteria.registerCriterion(criteria.ATReferenceCriterion, REFERENCE_INDICES + criteria.REFERENCE_INDICES)
criteria.registerCriterion(criteria.ATDateRangeCriterion, RELEVANT_INDICES)
criteria.registerCriterion(criteria.ATDateCriteria, DATE_INDICES + criteria.DATE_INDICES)
criteria.registerCriterion(criteria.ATBooleanCriterion, FIELD_INDICES + criteria.FIELD_INDICES)