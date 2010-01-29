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

def setCriterionIndices(criterion, indices):
    registry = criteria._criterionRegistry
    crit_id = criterion.meta_type
    registry[crit_id] = criterion
    registry.portaltypes[criterion.portal_type] = criterion

    registry.criterion2index[crit_id] = indices
    for index in indices:
        value = registry.index2criterion.get(index, ())
        registry.index2criterion[index] = value + (crit_id,)

setCriterionIndices(criteria.ATSortCriterion, SORT_INDICES + criteria.SORT_INDICES)
setCriterionIndices(criteria.ATSimpleStringCriterion, STRING_INDICES + criteria.STRING_INDICES)
setCriterionIndices(criteria.ATSimpleIntCriterion, LIST_INDICES + criteria.LIST_INDICES)
setCriterionIndices(criteria.ATSelectionCriterion, LIST_INDICES + criteria.LIST_INDICES)
setCriterionIndices(criteria.ATListCriterion, LIST_INDICES + criteria.LIST_INDICES)
setCriterionIndices(criteria.ATReferenceCriterion, REFERENCE_INDICES + criteria.REFERENCE_INDICES)
setCriterionIndices(criteria.ATDateRangeCriterion, RELEVANT_INDICES)
setCriterionIndices(criteria.ATDateCriteria, DATE_INDICES + criteria.DATE_INDICES)
setCriterionIndices(criteria.ATBooleanCriterion, FIELD_INDICES + criteria.FIELD_INDICES)