# InvoiceCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_uuid** | **str** |  | 
**invoice_date** | **str** |  | 
**due_date** | **str** |  | [optional] 
**subtotal** | [**Subtotal**](Subtotal.md) |  | 
**tax_amount** | [**TaxAmount**](TaxAmount.md) |  | [optional] 

## Example

```python
from clienthub.models.invoice_create import InvoiceCreate

# TODO update the JSON string below
json = "{}"
# create an instance of InvoiceCreate from a JSON string
invoice_create_instance = InvoiceCreate.from_json(json)
# print the JSON string representation of the object
print(InvoiceCreate.to_json())

# convert the object into a dict
invoice_create_dict = invoice_create_instance.to_dict()
# create an instance of InvoiceCreate from a dict
invoice_create_from_dict = InvoiceCreate.from_dict(invoice_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


