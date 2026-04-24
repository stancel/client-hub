# SourceUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**source_type** | **str** |  | [optional] 
**domain** | **str** |  | [optional] 
**description** | **str** |  | [optional] 

## Example

```python
from clienthub.models.source_update import SourceUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of SourceUpdate from a JSON string
source_update_instance = SourceUpdate.from_json(json)
# print the JSON string representation of the object
print(SourceUpdate.to_json())

# convert the object into a dict
source_update_dict = source_update_instance.to_dict()
# create an instance of SourceUpdate from a dict
source_update_from_dict = SourceUpdate.from_dict(source_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


