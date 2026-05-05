# LookupMatch


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**uuid** | **str** |  | 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**display_name** | **str** |  | [optional] 
**contact_type** | **str** |  | 
**organization** | **str** |  | [optional] 
**phone** | [**LookupMatchPhone**](LookupMatchPhone.md) |  | [optional] 
**email** | [**LookupMatchEmail**](LookupMatchEmail.md) |  | [optional] 
**phones** | [**List[LookupMatchPhone]**](LookupMatchPhone.md) |  | [optional] [default to []]
**emails** | [**List[LookupMatchEmail]**](LookupMatchEmail.md) |  | [optional] [default to []]
**recent_orders** | [**List[LookupMatchOrder]**](LookupMatchOrder.md) |  | [optional] [default to []]
**recent_communications** | [**List[LookupMatchCommunication]**](LookupMatchCommunication.md) |  | [optional] [default to []]
**tags** | **List[str]** |  | [optional] [default to []]
**channel_preferences** | [**Dict[str, LookupMatchChannelPref]**](LookupMatchChannelPref.md) |  | [optional] 

## Example

```python
from clienthub.models.lookup_match import LookupMatch

# TODO update the JSON string below
json = "{}"
# create an instance of LookupMatch from a JSON string
lookup_match_instance = LookupMatch.from_json(json)
# print the JSON string representation of the object
print(LookupMatch.to_json())

# convert the object into a dict
lookup_match_dict = lookup_match_instance.to_dict()
# create an instance of LookupMatch from a dict
lookup_match_from_dict = LookupMatch.from_dict(lookup_match_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


