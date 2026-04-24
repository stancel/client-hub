# AffiliationUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role_title** | **str** |  | [optional] 
**department** | **str** |  | [optional] 
**seniority** | **str** |  | [optional] 
**is_decision_maker** | **bool** |  | [optional] 
**is_primary** | **bool** |  | [optional] 
**start_date** | **date** |  | [optional] 
**end_date** | **date** |  | [optional] 
**is_active** | **bool** |  | [optional] 
**notes** | **str** |  | [optional] 
**external_refs_json** | **Dict[str, object]** |  | [optional] 

## Example

```python
from clienthub.models.affiliation_update import AffiliationUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of AffiliationUpdate from a JSON string
affiliation_update_instance = AffiliationUpdate.from_json(json)
# print the JSON string representation of the object
print(AffiliationUpdate.to_json())

# convert the object into a dict
affiliation_update_dict = affiliation_update_instance.to_dict()
# create an instance of AffiliationUpdate from a dict
affiliation_update_from_dict = AffiliationUpdate.from_dict(affiliation_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


