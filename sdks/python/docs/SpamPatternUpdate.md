# SpamPatternUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pattern** | **str** |  | [optional] 
**notes** | **str** |  | [optional] 
**is_active** | **bool** |  | [optional] 

## Example

```python
from clienthub.models.spam_pattern_update import SpamPatternUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of SpamPatternUpdate from a JSON string
spam_pattern_update_instance = SpamPatternUpdate.from_json(json)
# print the JSON string representation of the object
print(SpamPatternUpdate.to_json())

# convert the object into a dict
spam_pattern_update_dict = spam_pattern_update_instance.to_dict()
# create an instance of SpamPatternUpdate from a dict
spam_pattern_update_from_dict = SpamPatternUpdate.from_dict(spam_pattern_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


