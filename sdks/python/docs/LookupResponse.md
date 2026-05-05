# LookupResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**matches** | [**List[LookupMatch]**](LookupMatch.md) |  | 
**count** | **int** |  | 

## Example

```python
from clienthub.models.lookup_response import LookupResponse

# TODO update the JSON string below
json = "{}"
# create an instance of LookupResponse from a JSON string
lookup_response_instance = LookupResponse.from_json(json)
# print the JSON string representation of the object
print(LookupResponse.to_json())

# convert the object into a dict
lookup_response_dict = lookup_response_instance.to_dict()
# create an instance of LookupResponse from a dict
lookup_response_from_dict = LookupResponse.from_dict(lookup_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


