# PreferenceSet


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** |  | 
**data_source** | **str** |  | [optional] 

## Example

```python
from clienthub.models.preference_set import PreferenceSet

# TODO update the JSON string below
json = "{}"
# create an instance of PreferenceSet from a JSON string
preference_set_instance = PreferenceSet.from_json(json)
# print the JSON string representation of the object
print(PreferenceSet.to_json())

# convert the object into a dict
preference_set_dict = preference_set_instance.to_dict()
# create an instance of PreferenceSet from a dict
preference_set_from_dict = PreferenceSet.from_dict(preference_set_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


