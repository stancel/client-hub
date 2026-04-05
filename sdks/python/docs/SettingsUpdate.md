# SettingsUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**business_name** | **str** |  | [optional] 
**business_type** | **str** |  | [optional] 
**timezone** | **str** |  | [optional] 
**currency** | **str** |  | [optional] 
**tax_rate** | **float** |  | [optional] 
**phone** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**website** | **str** |  | [optional] 

## Example

```python
from clienthub.models.settings_update import SettingsUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of SettingsUpdate from a JSON string
settings_update_instance = SettingsUpdate.from_json(json)
# print the JSON string representation of the object
print(SettingsUpdate.to_json())

# convert the object into a dict
settings_update_dict = settings_update_instance.to_dict()
# create an instance of SettingsUpdate from a dict
settings_update_from_dict = SettingsUpdate.from_dict(settings_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


