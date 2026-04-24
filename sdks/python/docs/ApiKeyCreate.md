# ApiKeyCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] [default to 'Default key']

## Example

```python
from clienthub.models.api_key_create import ApiKeyCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ApiKeyCreate from a JSON string
api_key_create_instance = ApiKeyCreate.from_json(json)
# print the JSON string representation of the object
print(ApiKeyCreate.to_json())

# convert the object into a dict
api_key_create_dict = api_key_create_instance.to_dict()
# create an instance of ApiKeyCreate from a dict
api_key_create_from_dict = ApiKeyCreate.from_dict(api_key_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


