# # ContactCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **string** |  |
**last_name** | **string** |  |
**contact_type** | **string** |  | [optional] [default to 'prospect']
**display_name** | **string** |  | [optional]
**affiliations** | [**\ClientHub\Model\InlineAffiliationCreate[]**](InlineAffiliationCreate.md) |  | [optional]
**phones** | [**\ClientHub\Model\ContactCreatePhone[]**](ContactCreatePhone.md) |  | [optional]
**emails** | [**\ClientHub\Model\ContactCreateEmail[]**](ContactCreateEmail.md) |  | [optional]
**marketing_sources** | **string[]** |  | [optional]
**data_source** | **string** |  | [optional]
**external_refs_json** | **array<string,mixed>** |  | [optional]

[[Back to Model list]](../../README.md#models) [[Back to API list]](../../README.md#endpoints) [[Back to README]](../../README.md)
