# ClientHub\CommunicationsApi

All URIs are relative to http://localhost, except if the operation defines another base path.

| Method | HTTP request | Description |
| ------------- | ------------- | ------------- |
| [**createCommunicationApiV1CommunicationsPost()**](CommunicationsApi.md#createCommunicationApiV1CommunicationsPost) | **POST** /api/v1/communications | Create Communication |
| [**getCommunicationApiV1CommunicationsUuidGet()**](CommunicationsApi.md#getCommunicationApiV1CommunicationsUuidGet) | **GET** /api/v1/communications/{uuid} | Get Communication |
| [**listCommunicationsApiV1CommunicationsGet()**](CommunicationsApi.md#listCommunicationsApiV1CommunicationsGet) | **GET** /api/v1/communications | List Communications |


## `createCommunicationApiV1CommunicationsPost()`

```php
createCommunicationApiV1CommunicationsPost($comm_create): mixed
```

Create Communication

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\CommunicationsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$comm_create = new \ClientHub\Model\CommCreate(); // \ClientHub\Model\CommCreate

try {
    $result = $apiInstance->createCommunicationApiV1CommunicationsPost($comm_create);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling CommunicationsApi->createCommunicationApiV1CommunicationsPost: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **comm_create** | [**\ClientHub\Model\CommCreate**](../Model/CommCreate.md)|  | |

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

## `getCommunicationApiV1CommunicationsUuidGet()`

```php
getCommunicationApiV1CommunicationsUuidGet($uuid): mixed
```

Get Communication

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\CommunicationsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $result = $apiInstance->getCommunicationApiV1CommunicationsUuidGet($uuid);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling CommunicationsApi->getCommunicationApiV1CommunicationsUuidGet: ', $e->getMessage(), PHP_EOL;
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

## `listCommunicationsApiV1CommunicationsGet()`

```php
listCommunicationsApiV1CommunicationsGet($page, $per_page, $contact_uuid, $channel, $direction): mixed
```

List Communications

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\CommunicationsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$page = 1; // int
$per_page = 25; // int
$contact_uuid = 'contact_uuid_example'; // string
$channel = 'channel_example'; // string
$direction = 'direction_example'; // string

try {
    $result = $apiInstance->listCommunicationsApiV1CommunicationsGet($page, $per_page, $contact_uuid, $channel, $direction);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling CommunicationsApi->listCommunicationsApiV1CommunicationsGet: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **page** | **int**|  | [optional] [default to 1] |
| **per_page** | **int**|  | [optional] [default to 25] |
| **contact_uuid** | **string**|  | [optional] |
| **channel** | **string**|  | [optional] |
| **direction** | **string**|  | [optional] |

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
