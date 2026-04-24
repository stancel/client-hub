# ContactCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** |  | 
**last_name** | **str** |  | 
**contact_type** | **str** |  | [optional] [default to 'prospect']
**display_name** | **str** |  | [optional] 
**affiliations** | [**List[InlineAffiliationCreate]**](InlineAffiliationCreate.md) |  | [optional] [default to []]
**phones** | [**List[ContactCreatePhone]**](ContactCreatePhone.md) |  | [optional] [default to []]
**emails** | [**List[ContactCreateEmail]**](ContactCreateEmail.md) |  | [optional] [default to []]
**marketing_sources** | **List[str]** |  | [optional] [default to []]
**data_source** | **str** |  | [optional] 
**external_refs_json** | **Dict[str, object]** |  | [optional] 

## Example

```python
from clienthub.models.contact_create import ContactCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ContactCreate from a JSON string
contact_create_instance = ContactCreate.from_json(json)
# print the JSON string representation of the object
print(ContactCreate.to_json())

# convert the object into a dict
contact_create_dict = contact_create_instance.to_dict()
# create an instance of ContactCreate from a dict
contact_create_from_dict = ContactCreate.from_dict(contact_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


