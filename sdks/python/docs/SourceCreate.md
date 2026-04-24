# SourceCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** |  | 
**name** | **str** |  | 
**source_type** | **str** |  | [optional] [default to 'website']
**domain** | **str** |  | [optional] 
**description** | **str** |  | [optional] 

## Example

```python
from clienthub.models.source_create import SourceCreate

# TODO update the JSON string below
json = "{}"
# create an instance of SourceCreate from a JSON string
source_create_instance = SourceCreate.from_json(json)
# print the JSON string representation of the object
print(SourceCreate.to_json())

# convert the object into a dict
source_create_dict = source_create_instance.to_dict()
# create an instance of SourceCreate from a dict
source_create_from_dict = SourceCreate.from_dict(source_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


