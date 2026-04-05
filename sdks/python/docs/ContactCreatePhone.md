# ContactCreatePhone


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**number** | **str** |  | 
**type** | **str** |  | [optional] [default to 'mobile']
**is_primary** | **bool** |  | [optional] [default to False]

## Example

```python
from clienthub.models.contact_create_phone import ContactCreatePhone

# TODO update the JSON string below
json = "{}"
# create an instance of ContactCreatePhone from a JSON string
contact_create_phone_instance = ContactCreatePhone.from_json(json)
# print the JSON string representation of the object
print(ContactCreatePhone.to_json())

# convert the object into a dict
contact_create_phone_dict = contact_create_phone_instance.to_dict()
# create an instance of ContactCreatePhone from a dict
contact_create_phone_from_dict = ContactCreatePhone.from_dict(contact_create_phone_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


