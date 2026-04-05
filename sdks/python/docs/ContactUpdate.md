# ContactUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**display_name** | **str** |  | [optional] 
**contact_type** | **str** |  | [optional] 
**organization_uuid** | **str** |  | [optional] 
**enrichment_status** | **str** |  | [optional] 
**notes_text** | **str** |  | [optional] 

## Example

```python
from clienthub.models.contact_update import ContactUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of ContactUpdate from a JSON string
contact_update_instance = ContactUpdate.from_json(json)
# print the JSON string representation of the object
print(ContactUpdate.to_json())

# convert the object into a dict
contact_update_dict = contact_update_instance.to_dict()
# create an instance of ContactUpdate from a dict
contact_update_from_dict = ContactUpdate.from_dict(contact_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


