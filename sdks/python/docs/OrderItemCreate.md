# OrderItemCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | 
**item_type** | **str** |  | [optional] [default to 'product']
**quantity** | [**Quantity**](Quantity.md) |  | [optional] 
**unit_price** | [**UnitPrice**](UnitPrice.md) |  | 
**discount_amount** | [**DiscountAmount**](DiscountAmount.md) |  | [optional] 

## Example

```python
from clienthub.models.order_item_create import OrderItemCreate

# TODO update the JSON string below
json = "{}"
# create an instance of OrderItemCreate from a JSON string
order_item_create_instance = OrderItemCreate.from_json(json)
# print the JSON string representation of the object
print(OrderItemCreate.to_json())

# convert the object into a dict
order_item_create_dict = order_item_create_instance.to_dict()
# create an instance of OrderItemCreate from a dict
order_item_create_from_dict = OrderItemCreate.from_dict(order_item_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


