# CommCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**contact_uuid** | **str** |  | 
**channel** | **str** |  | 
**direction** | **str** |  | 
**occurred_at** | **str** |  | 
**subject** | **str** |  | [optional] 
**body** | **str** |  | [optional] 
**order_uuid** | **str** |  | [optional] 
**external_message_id** | **str** |  | [optional] 
**created_by** | **str** |  | [optional] 

## Example

```python
from clienthub.models.comm_create import CommCreate

# TODO update the JSON string below
json = "{}"
# create an instance of CommCreate from a JSON string
comm_create_instance = CommCreate.from_json(json)
# print the JSON string representation of the object
print(CommCreate.to_json())

# convert the object into a dict
comm_create_dict = comm_create_instance.to_dict()
# create an instance of CommCreate from a dict
comm_create_from_dict = CommCreate.from_dict(comm_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


