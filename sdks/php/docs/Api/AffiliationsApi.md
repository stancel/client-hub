# ClientHub\AffiliationsApi

All URIs are relative to http://localhost, except if the operation defines another base path.

| Method | HTTP request | Description |
| ------------- | ------------- | ------------- |
| [**createAffiliationEndpointApiV1ContactsContactUuidAffiliationsPost()**](AffiliationsApi.md#createAffiliationEndpointApiV1ContactsContactUuidAffiliationsPost) | **POST** /api/v1/contacts/{contact_uuid}/affiliations | Create Affiliation Endpoint |
| [**deleteAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidDelete()**](AffiliationsApi.md#deleteAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidDelete) | **DELETE** /api/v1/contacts/{contact_uuid}/affiliations/{affiliation_uuid} | Delete Affiliation Endpoint |
| [**listAffiliationsEndpointApiV1ContactsContactUuidAffiliationsGet()**](AffiliationsApi.md#listAffiliationsEndpointApiV1ContactsContactUuidAffiliationsGet) | **GET** /api/v1/contacts/{contact_uuid}/affiliations | List Affiliations Endpoint |
| [**updateAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidPut()**](AffiliationsApi.md#updateAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidPut) | **PUT** /api/v1/contacts/{contact_uuid}/affiliations/{affiliation_uuid} | Update Affiliation Endpoint |


## `createAffiliationEndpointApiV1ContactsContactUuidAffiliationsPost()`

```php
createAffiliationEndpointApiV1ContactsContactUuidAffiliationsPost($contact_uuid, $affiliation_create): mixed
```

Create Affiliation Endpoint

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AffiliationsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$contact_uuid = 'contact_uuid_example'; // string
$affiliation_create = new \ClientHub\Model\AffiliationCreate(); // \ClientHub\Model\AffiliationCreate

try {
    $result = $apiInstance->createAffiliationEndpointApiV1ContactsContactUuidAffiliationsPost($contact_uuid, $affiliation_create);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AffiliationsApi->createAffiliationEndpointApiV1ContactsContactUuidAffiliationsPost: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **contact_uuid** | **string**|  | |
| **affiliation_create** | [**\ClientHub\Model\AffiliationCreate**](../Model/AffiliationCreate.md)|  | |

### Return type

**mixed**

### Authorization

[APIKeyHeader](../../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)

## `deleteAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidDelete()`

```php
deleteAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidDelete($contact_uuid, $affiliation_uuid)
```

Delete Affiliation Endpoint

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AffiliationsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$contact_uuid = 'contact_uuid_example'; // string
$affiliation_uuid = 'affiliation_uuid_example'; // string

try {
    $apiInstance->deleteAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidDelete($contact_uuid, $affiliation_uuid);
} catch (Exception $e) {
    echo 'Exception when calling AffiliationsApi->deleteAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidDelete: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **contact_uuid** | **string**|  | |
| **affiliation_uuid** | **string**|  | |

### Return type

void (empty response body)

### Authorization

[APIKeyHeader](../../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)

## `listAffiliationsEndpointApiV1ContactsContactUuidAffiliationsGet()`

```php
listAffiliationsEndpointApiV1ContactsContactUuidAffiliationsGet($contact_uuid, $active_only): mixed
```

List Affiliations Endpoint

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AffiliationsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$contact_uuid = 'contact_uuid_example'; // string
$active_only = true; // bool

try {
    $result = $apiInstance->listAffiliationsEndpointApiV1ContactsContactUuidAffiliationsGet($contact_uuid, $active_only);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AffiliationsApi->listAffiliationsEndpointApiV1ContactsContactUuidAffiliationsGet: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **contact_uuid** | **string**|  | |
| **active_only** | **bool**|  | [optional] [default to true] |

### Return type

**mixed**

### Authorization

[APIKeyHeader](../../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)

## `updateAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidPut()`

```php
updateAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidPut($contact_uuid, $affiliation_uuid, $affiliation_update): mixed
```

Update Affiliation Endpoint

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AffiliationsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$contact_uuid = 'contact_uuid_example'; // string
$affiliation_uuid = 'affiliation_uuid_example'; // string
$affiliation_update = new \ClientHub\Model\AffiliationUpdate(); // \ClientHub\Model\AffiliationUpdate

try {
    $result = $apiInstance->updateAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidPut($contact_uuid, $affiliation_uuid, $affiliation_update);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AffiliationsApi->updateAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidPut: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **contact_uuid** | **string**|  | |
| **affiliation_uuid** | **string**|  | |
| **affiliation_update** | [**\ClientHub\Model\AffiliationUpdate**](../Model/AffiliationUpdate.md)|  | |

### Return type

**mixed**

### Authorization

[APIKeyHeader](../../README.md#APIKeyHeader)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`

[[Back to top]](#) [[Back to API list]](../../README.md#endpoints)
[[Back to Model list]](../../README.md#models)
[[Back to README]](../../README.md)
