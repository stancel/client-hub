# AffiliationCreate


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
**notes** | **str** |  | [optional] 
**external_refs_json** | **Dict[str, object]** |  | [optional] 

## Example

```python
from clienthub.models.affiliation_create import AffiliationCreate

# TODO update the JSON string below
json = "{}"
# create an instance of AffiliationCreate from a JSON string
affiliation_create_instance = AffiliationCreate.from_json(json)
# print the JSON string representation of the object
print(AffiliationCreate.to_json())

# convert the object into a dict
affiliation_create_dict = affiliation_create_instance.to_dict()
# create an instance of AffiliationCreate from a dict
affiliation_create_from_dict = AffiliationCreate.from_dict(affiliation_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


