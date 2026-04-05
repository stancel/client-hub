# PaymentCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | [**Amount**](Amount.md) |  | 
**payment_date** | **str** |  | 
**payment_method** | **str** |  | [optional] [default to 'online']
**reference_number** | **str** |  | [optional] 
**external_payment_id** | **str** |  | [optional] 

## Example

```python
from clienthub.models.payment_create import PaymentCreate

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentCreate from a JSON string
payment_create_instance = PaymentCreate.from_json(json)
# print the JSON string representation of the object
print(PaymentCreate.to_json())

# convert the object into a dict
payment_create_dict = payment_create_instance.to_dict()
# create an instance of PaymentCreate from a dict
payment_create_from_dict = PaymentCreate.from_dict(payment_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


