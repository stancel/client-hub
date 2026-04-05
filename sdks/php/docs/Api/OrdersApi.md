# ClientHub\OrdersApi

All URIs are relative to http://localhost, except if the operation defines another base path.

| Method | HTTP request | Description |
| ------------- | ------------- | ------------- |
| [**changeOrderStatusApiV1OrdersUuidStatusPost()**](OrdersApi.md#changeOrderStatusApiV1OrdersUuidStatusPost) | **POST** /api/v1/orders/{uuid}/status | Change Order Status |
| [**createOrderApiV1OrdersPost()**](OrdersApi.md#createOrderApiV1OrdersPost) | **POST** /api/v1/orders | Create Order |
| [**deleteOrderApiV1OrdersUuidDelete()**](OrdersApi.md#deleteOrderApiV1OrdersUuidDelete) | **DELETE** /api/v1/orders/{uuid} | Delete Order |
| [**getOrderApiV1OrdersUuidGet()**](OrdersApi.md#getOrderApiV1OrdersUuidGet) | **GET** /api/v1/orders/{uuid} | Get Order |
| [**listOrdersApiV1OrdersGet()**](OrdersApi.md#listOrdersApiV1OrdersGet) | **GET** /api/v1/orders | List Orders |


## `changeOrderStatusApiV1OrdersUuidStatusPost()`

```php
changeOrderStatusApiV1OrdersUuidStatusPost($uuid, $status_change): mixed
```

Change Order Status

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\OrdersApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string
$status_change = new \ClientHub\Model\StatusChange(); // \ClientHub\Model\StatusChange

try {
    $result = $apiInstance->changeOrderStatusApiV1OrdersUuidStatusPost($uuid, $status_change);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling OrdersApi->changeOrderStatusApiV1OrdersUuidStatusPost: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **uuid** | **string**|  | |
| **status_change** | [**\ClientHub\Model\StatusChange**](../Model/StatusChange.md)|  | |

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

## `createOrderApiV1OrdersPost()`

```php
createOrderApiV1OrdersPost($order_create): mixed
```

Create Order

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\OrdersApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$order_create = new \ClientHub\Model\OrderCreate(); // \ClientHub\Model\OrderCreate

try {
    $result = $apiInstance->createOrderApiV1OrdersPost($order_create);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling OrdersApi->createOrderApiV1OrdersPost: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **order_create** | [**\ClientHub\Model\OrderCreate**](../Model/OrderCreate.md)|  | |

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

## `deleteOrderApiV1OrdersUuidDelete()`

```php
deleteOrderApiV1OrdersUuidDelete($uuid)
```

Delete Order

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\OrdersApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $apiInstance->deleteOrderApiV1OrdersUuidDelete($uuid);
} catch (Exception $e) {
    echo 'Exception when calling OrdersApi->deleteOrderApiV1OrdersUuidDelete: ', $e->getMessage(), PHP_EOL;
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

## `getOrderApiV1OrdersUuidGet()`

```php
getOrderApiV1OrdersUuidGet($uuid): mixed
```

Get Order

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\OrdersApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $result = $apiInstance->getOrderApiV1OrdersUuidGet($uuid);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling OrdersApi->getOrderApiV1OrdersUuidGet: ', $e->getMessage(), PHP_EOL;
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

## `listOrdersApiV1OrdersGet()`

```php
listOrdersApiV1OrdersGet($page, $per_page, $status, $contact_uuid): mixed
```

List Orders

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\OrdersApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$page = 1; // int
$per_page = 25; // int
$status = 'status_example'; // string
$contact_uuid = 'contact_uuid_example'; // string

try {
    $result = $apiInstance->listOrdersApiV1OrdersGet($page, $per_page, $status, $contact_uuid);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling OrdersApi->listOrdersApiV1OrdersGet: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **page** | **int**|  | [optional] [default to 1] |
| **per_page** | **int**|  | [optional] [default to 25] |
| **status** | **string**|  | [optional] |
| **contact_uuid** | **string**|  | [optional] |

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
