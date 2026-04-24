# InlineAffiliationCreate

Embedded in ContactCreate for one-shot contact + affiliation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_uuid** | **str** |  | 
**role_title** | **str** |  | [optional] 
**department** | **str** |  | [optional] 
**seniority** | **str** |  | [optional] 
**is_decision_maker** | **bool** |  | [optional] [default to False]
**is_primary** | **bool** |  | [optional] [default to False]
**start_date** | **date** |  | [optional] 
**end_date** | **date** |  | [optional] 

## Example

```python
from clienthub.models.inline_affiliation_create import InlineAffiliationCreate

# TODO update the JSON string below
json = "{}"
# create an instance of InlineAffiliationCreate from a JSON string
inline_affiliation_create_instance = InlineAffiliationCreate.from_json(json)
# print the JSON string representation of the object
print(InlineAffiliationCreate.to_json())

# convert the object into a dict
inline_affiliation_create_dict = inline_affiliation_create_instance.to_dict()
# create an instance of InlineAffiliationCreate from a dict
inline_affiliation_create_from_dict = InlineAffiliationCreate.from_dict(inline_affiliation_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


