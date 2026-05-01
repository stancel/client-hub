# SpamPatternCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pattern_kind** | **str** |  | 
**pattern** | **str** |  | 
**notes** | **str** |  | [optional] 
**is_active** | **bool** |  | [optional] [default to True]

## Example

```python
from clienthub.models.spam_pattern_create import SpamPatternCreate

# TODO update the JSON string below
json = "{}"
# create an instance of SpamPatternCreate from a JSON string
spam_pattern_create_instance = SpamPatternCreate.from_json(json)
# print the JSON string representation of the object
print(SpamPatternCreate.to_json())

# convert the object into a dict
spam_pattern_create_dict = spam_pattern_create_instance.to_dict()
# create an instance of SpamPatternCreate from a dict
spam_pattern_create_from_dict = SpamPatternCreate.from_dict(spam_pattern_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


