# LookupMatchPhone


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**number** | **str** |  | 
**type** | **str** |  | 
**is_primary** | **bool** |  | 
**is_verified** | **bool** |  | 

## Example

```python
from clienthub.models.lookup_match_phone import LookupMatchPhone

# TODO update the JSON string below
json = "{}"
# create an instance of LookupMatchPhone from a JSON string
lookup_match_phone_instance = LookupMatchPhone.from_json(json)
# print the JSON string representation of the object
print(LookupMatchPhone.to_json())

# convert the object into a dict
lookup_match_phone_dict = lookup_match_phone_instance.to_dict()
# create an instance of LookupMatchPhone from a dict
lookup_match_phone_from_dict = LookupMatchPhone.from_dict(lookup_match_phone_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


