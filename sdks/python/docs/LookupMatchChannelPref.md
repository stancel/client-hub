# LookupMatchChannelPref


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**preferred** | **bool** |  | 
**opt_in** | [**AnyOf**](AnyOf.md) |  | [optional] 

## Example

```python
from clienthub.models.lookup_match_channel_pref import LookupMatchChannelPref

# TODO update the JSON string below
json = "{}"
# create an instance of LookupMatchChannelPref from a JSON string
lookup_match_channel_pref_instance = LookupMatchChannelPref.from_json(json)
# print the JSON string representation of the object
print(LookupMatchChannelPref.to_json())

# convert the object into a dict
lookup_match_channel_pref_dict = lookup_match_channel_pref_instance.to_dict()
# create an instance of LookupMatchChannelPref from a dict
lookup_match_channel_pref_from_dict = LookupMatchChannelPref.from_dict(lookup_match_channel_pref_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


