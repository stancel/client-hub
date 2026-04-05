# MarketingOptOuts


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**opt_out_sms** | **bool** |  | 
**opt_out_email** | **bool** |  | 
**opt_out_phone** | **bool** |  | 

## Example

```python
from clienthub.models.marketing_opt_outs import MarketingOptOuts

# TODO update the JSON string below
json = "{}"
# create an instance of MarketingOptOuts from a JSON string
marketing_opt_outs_instance = MarketingOptOuts.from_json(json)
# print the JSON string representation of the object
print(MarketingOptOuts.to_json())

# convert the object into a dict
marketing_opt_outs_dict = marketing_opt_outs_instance.to_dict()
# create an instance of MarketingOptOuts from a dict
marketing_opt_outs_from_dict = MarketingOptOuts.from_dict(marketing_opt_outs_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


