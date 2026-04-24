# ClientHub\AdminApi

All URIs are relative to http://localhost, except if the operation defines another base path.

| Method | HTTP request | Description |
| ------------- | ------------- | ------------- |
| [**createApiKeyApiV1AdminSourcesUuidApiKeysPost()**](AdminApi.md#createApiKeyApiV1AdminSourcesUuidApiKeysPost) | **POST** /api/v1/admin/sources/{uuid}/api-keys | Create Api Key |
| [**createSourceApiV1AdminSourcesPost()**](AdminApi.md#createSourceApiV1AdminSourcesPost) | **POST** /api/v1/admin/sources | Create Source |
| [**deleteSourceApiV1AdminSourcesUuidDelete()**](AdminApi.md#deleteSourceApiV1AdminSourcesUuidDelete) | **DELETE** /api/v1/admin/sources/{uuid} | Delete Source |
| [**getSourceApiV1AdminSourcesUuidGet()**](AdminApi.md#getSourceApiV1AdminSourcesUuidGet) | **GET** /api/v1/admin/sources/{uuid} | Get Source |
| [**listApiKeysApiV1AdminSourcesUuidApiKeysGet()**](AdminApi.md#listApiKeysApiV1AdminSourcesUuidApiKeysGet) | **GET** /api/v1/admin/sources/{uuid}/api-keys | List Api Keys |
| [**listEventsApiV1AdminEventsGet()**](AdminApi.md#listEventsApiV1AdminEventsGet) | **GET** /api/v1/admin/events | List Events |
| [**listSourcesApiV1AdminSourcesGet()**](AdminApi.md#listSourcesApiV1AdminSourcesGet) | **GET** /api/v1/admin/sources | List Sources |
| [**revokeApiKeyApiV1AdminApiKeysUuidDelete()**](AdminApi.md#revokeApiKeyApiV1AdminApiKeysUuidDelete) | **DELETE** /api/v1/admin/api-keys/{uuid} | Revoke Api Key |
| [**updateSourceApiV1AdminSourcesUuidPut()**](AdminApi.md#updateSourceApiV1AdminSourcesUuidPut) | **PUT** /api/v1/admin/sources/{uuid} | Update Source |


## `createApiKeyApiV1AdminSourcesUuidApiKeysPost()`

```php
createApiKeyApiV1AdminSourcesUuidApiKeysPost($uuid, $api_key_create): mixed
```

Create Api Key

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string
$api_key_create = new \ClientHub\Model\ApiKeyCreate(); // \ClientHub\Model\ApiKeyCreate

try {
    $result = $apiInstance->createApiKeyApiV1AdminSourcesUuidApiKeysPost($uuid, $api_key_create);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AdminApi->createApiKeyApiV1AdminSourcesUuidApiKeysPost: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **uuid** | **string**|  | |
| **api_key_create** | [**\ClientHub\Model\ApiKeyCreate**](../Model/ApiKeyCreate.md)|  | |

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

## `createSourceApiV1AdminSourcesPost()`

```php
createSourceApiV1AdminSourcesPost($source_create): mixed
```

Create Source

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$source_create = new \ClientHub\Model\SourceCreate(); // \ClientHub\Model\SourceCreate

try {
    $result = $apiInstance->createSourceApiV1AdminSourcesPost($source_create);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AdminApi->createSourceApiV1AdminSourcesPost: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **source_create** | [**\ClientHub\Model\SourceCreate**](../Model/SourceCreate.md)|  | |

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

## `deleteSourceApiV1AdminSourcesUuidDelete()`

```php
deleteSourceApiV1AdminSourcesUuidDelete($uuid)
```

Delete Source

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $apiInstance->deleteSourceApiV1AdminSourcesUuidDelete($uuid);
} catch (Exception $e) {
    echo 'Exception when calling AdminApi->deleteSourceApiV1AdminSourcesUuidDelete: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **uuid** | **string**|  | |

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

## `getSourceApiV1AdminSourcesUuidGet()`

```php
getSourceApiV1AdminSourcesUuidGet($uuid): mixed
```

Get Source

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $result = $apiInstance->getSourceApiV1AdminSourcesUuidGet($uuid);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AdminApi->getSourceApiV1AdminSourcesUuidGet: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **uuid** | **string**|  | |

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

## `listApiKeysApiV1AdminSourcesUuidApiKeysGet()`

```php
listApiKeysApiV1AdminSourcesUuidApiKeysGet($uuid): mixed
```

List Api Keys

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $result = $apiInstance->listApiKeysApiV1AdminSourcesUuidApiKeysGet($uuid);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AdminApi->listApiKeysApiV1AdminSourcesUuidApiKeysGet: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **uuid** | **string**|  | |

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

## `listEventsApiV1AdminEventsGet()`

```php
listEventsApiV1AdminEventsGet($source_code, $channel_code, $date_from, $date_to, $limit): mixed
```

List Events

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$source_code = 'source_code_example'; // string
$channel_code = 'channel_code_example'; // string
$date_from = 'date_from_example'; // string
$date_to = 'date_to_example'; // string
$limit = 100; // int

try {
    $result = $apiInstance->listEventsApiV1AdminEventsGet($source_code, $channel_code, $date_from, $date_to, $limit);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AdminApi->listEventsApiV1AdminEventsGet: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **source_code** | **string**|  | [optional] |
| **channel_code** | **string**|  | [optional] |
| **date_from** | **string**|  | [optional] |
| **date_to** | **string**|  | [optional] |
| **limit** | **int**|  | [optional] [default to 100] |

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

## `listSourcesApiV1AdminSourcesGet()`

```php
listSourcesApiV1AdminSourcesGet(): mixed
```

List Sources

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);

try {
    $result = $apiInstance->listSourcesApiV1AdminSourcesGet();
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AdminApi->listSourcesApiV1AdminSourcesGet: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

This endpoint does not need any parameter.

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

## `revokeApiKeyApiV1AdminApiKeysUuidDelete()`

```php
revokeApiKeyApiV1AdminApiKeysUuidDelete($uuid)
```

Revoke Api Key

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $apiInstance->revokeApiKeyApiV1AdminApiKeysUuidDelete($uuid);
} catch (Exception $e) {
    echo 'Exception when calling AdminApi->revokeApiKeyApiV1AdminApiKeysUuidDelete: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **uuid** | **string**|  | |

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

## `updateSourceApiV1AdminSourcesUuidPut()`

```php
updateSourceApiV1AdminSourcesUuidPut($uuid, $source_update): mixed
```

Update Source

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string
$source_update = new \ClientHub\Model\SourceUpdate(); // \ClientHub\Model\SourceUpdate

try {
    $result = $apiInstance->updateSourceApiV1AdminSourcesUuidPut($uuid, $source_update);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AdminApi->updateSourceApiV1AdminSourcesUuidPut: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **uuid** | **string**|  | |
| **source_update** | [**\ClientHub\Model\SourceUpdate**](../Model/SourceUpdate.md)|  | |

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
