# ContactCreateEmail


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address** | **str** |  | 
**type** | **str** |  | [optional] [default to 'personal']
**is_primary** | **bool** |  | [optional] [default to False]

## Example

```python
from clienthub.models.contact_create_email import ContactCreateEmail

# TODO update the JSON string below
json = "{}"
# create an instance of ContactCreateEmail from a JSON string
contact_create_email_instance = ContactCreateEmail.from_json(json)
# print the JSON string representation of the object
print(ContactCreateEmail.to_json())

# convert the object into a dict
contact_create_email_dict = contact_create_email_instance.to_dict()
# create an instance of ContactCreateEmail from a dict
contact_create_email_from_dict = ContactCreateEmail.from_dict(contact_create_email_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


