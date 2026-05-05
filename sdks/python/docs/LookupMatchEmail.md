# LookupMatchEmail


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address** | **str** |  | 
**type** | **str** |  | 
**is_primary** | **bool** |  | 
**is_verified** | **bool** |  | 

## Example

```python
from clienthub.models.lookup_match_email import LookupMatchEmail

# TODO update the JSON string below
json = "{}"
# create an instance of LookupMatchEmail from a JSON string
lookup_match_email_instance = LookupMatchEmail.from_json(json)
# print the JSON string representation of the object
print(LookupMatchEmail.to_json())

# convert the object into a dict
lookup_match_email_dict = lookup_match_email_instance.to_dict()
# create an instance of LookupMatchEmail from a dict
lookup_match_email_from_dict = LookupMatchEmail.from_dict(lookup_match_email_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


