# LookupMatchCommunication


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**channel** | **str** |  | 
**direction** | **str** |  | 
**subject** | **str** |  | [optional] 
**occurred_at** | **str** |  | [optional] 

## Example

```python
from clienthub.models.lookup_match_communication import LookupMatchCommunication

# TODO update the JSON string below
json = "{}"
# create an instance of LookupMatchCommunication from a JSON string
lookup_match_communication_instance = LookupMatchCommunication.from_json(json)
# print the JSON string representation of the object
print(LookupMatchCommunication.to_json())

# convert the object into a dict
lookup_match_communication_dict = lookup_match_communication_instance.to_dict()
# create an instance of LookupMatchCommunication from a dict
lookup_match_communication_from_dict = LookupMatchCommunication.from_dict(lookup_match_communication_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


