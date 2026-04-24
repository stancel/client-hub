# OrderCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**contact_uuid** | **str** |  | 
**order_date** | **str** |  | 
**due_date** | **str** |  | [optional] 
**scheduled_at** | **str** |  | [optional] 
**items** | [**List[OrderItemCreate]**](OrderItemCreate.md) |  | [optional] [default to []]
**notes_text** | **str** |  | [optional] 
**external_refs_json** | **Dict[str, object]** |  | [optional] 

## Example

```python
from clienthub.models.order_create import OrderCreate

# TODO update the JSON string below
json = "{}"
# create an instance of OrderCreate from a JSON string
order_create_instance = OrderCreate.from_json(json)
# print the JSON string representation of the object
print(OrderCreate.to_json())

# convert the object into a dict
order_create_dict = order_create_instance.to_dict()
# create an instance of OrderCreate from a dict
order_create_from_dict = OrderCreate.from_dict(order_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


