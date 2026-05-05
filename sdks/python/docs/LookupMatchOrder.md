# LookupMatchOrder


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_number** | **str** |  | [optional] 
**status** | **str** |  | 
**total** | **str** |  | 
**order_date** | **str** |  | 

## Example

```python
from clienthub.models.lookup_match_order import LookupMatchOrder

# TODO update the JSON string below
json = "{}"
# create an instance of LookupMatchOrder from a JSON string
lookup_match_order_instance = LookupMatchOrder.from_json(json)
# print the JSON string representation of the object
print(LookupMatchOrder.to_json())

# convert the object into a dict
lookup_match_order_dict = lookup_match_order_instance.to_dict()
# create an instance of LookupMatchOrder from a dict
lookup_match_order_from_dict = LookupMatchOrder.from_dict(lookup_match_order_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


