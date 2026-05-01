# ClientHub\SpamAdminApi

All URIs are relative to http://localhost, except if the operation defines another base path.

| Method | HTTP request | Description |
| ------------- | ------------- | ------------- |
| [**adminCreatePatternApiV1AdminSpamPatternsPost()**](SpamAdminApi.md#adminCreatePatternApiV1AdminSpamPatternsPost) | **POST** /api/v1/admin/spam-patterns | Admin Create Pattern |
| [**adminDeletePatternApiV1AdminSpamPatternsUuidDelete()**](SpamAdminApi.md#adminDeletePatternApiV1AdminSpamPatternsUuidDelete) | **DELETE** /api/v1/admin/spam-patterns/{uuid} | Admin Delete Pattern |
| [**adminEventStatsApiV1AdminSpamEventsStatsGet()**](SpamAdminApi.md#adminEventStatsApiV1AdminSpamEventsStatsGet) | **GET** /api/v1/admin/spam-events/stats | Admin Event Stats |
| [**adminListEventsApiV1AdminSpamEventsGet()**](SpamAdminApi.md#adminListEventsApiV1AdminSpamEventsGet) | **GET** /api/v1/admin/spam-events | Admin List Events |
| [**adminListPatternsApiV1AdminSpamPatternsGet()**](SpamAdminApi.md#adminListPatternsApiV1AdminSpamPatternsGet) | **GET** /api/v1/admin/spam-patterns | Admin List Patterns |
| [**adminMarkEventFalsePositiveApiV1AdminSpamEventsUuidMarkFalsePositivePost()**](SpamAdminApi.md#adminMarkEventFalsePositiveApiV1AdminSpamEventsUuidMarkFalsePositivePost) | **POST** /api/v1/admin/spam-events/{uuid}/mark-false-positive | Admin Mark Event False Positive |
| [**adminUpdatePatternApiV1AdminSpamPatternsUuidPut()**](SpamAdminApi.md#adminUpdatePatternApiV1AdminSpamPatternsUuidPut) | **PUT** /api/v1/admin/spam-patterns/{uuid} | Admin Update Pattern |


## `adminCreatePatternApiV1AdminSpamPatternsPost()`

```php
adminCreatePatternApiV1AdminSpamPatternsPost($spam_pattern_create): mixed
```

Admin Create Pattern

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\SpamAdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$spam_pattern_create = new \ClientHub\Model\SpamPatternCreate(); // \ClientHub\Model\SpamPatternCreate

try {
    $result = $apiInstance->adminCreatePatternApiV1AdminSpamPatternsPost($spam_pattern_create);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling SpamAdminApi->adminCreatePatternApiV1AdminSpamPatternsPost: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **spam_pattern_create** | [**\ClientHub\Model\SpamPatternCreate**](../Model/SpamPatternCreate.md)|  | |

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

## `adminDeletePatternApiV1AdminSpamPatternsUuidDelete()`

```php
adminDeletePatternApiV1AdminSpamPatternsUuidDelete($uuid)
```

Admin Delete Pattern

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\SpamAdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $apiInstance->adminDeletePatternApiV1AdminSpamPatternsUuidDelete($uuid);
} catch (Exception $e) {
    echo 'Exception when calling SpamAdminApi->adminDeletePatternApiV1AdminSpamPatternsUuidDelete: ', $e->getMessage(), PHP_EOL;
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

## `adminEventStatsApiV1AdminSpamEventsStatsGet()`

```php
adminEventStatsApiV1AdminSpamEventsStatsGet(): mixed
```

Admin Event Stats

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\SpamAdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);

try {
    $result = $apiInstance->adminEventStatsApiV1AdminSpamEventsStatsGet();
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling SpamAdminApi->adminEventStatsApiV1AdminSpamEventsStatsGet: ', $e->getMessage(), PHP_EOL;
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

## `adminListEventsApiV1AdminSpamEventsGet()`

```php
adminListEventsApiV1AdminSpamEventsGet($page, $per_page, $endpoint, $integration_kind, $rejection_reason, $submitted_email, $was_false_positive): mixed
```

Admin List Events

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\SpamAdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$page = 1; // int
$per_page = 50; // int
$endpoint = 'endpoint_example'; // string
$integration_kind = 'integration_kind_example'; // string
$rejection_reason = 'rejection_reason_example'; // string
$submitted_email = 'submitted_email_example'; // string
$was_false_positive = True; // bool

try {
    $result = $apiInstance->adminListEventsApiV1AdminSpamEventsGet($page, $per_page, $endpoint, $integration_kind, $rejection_reason, $submitted_email, $was_false_positive);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling SpamAdminApi->adminListEventsApiV1AdminSpamEventsGet: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **page** | **int**|  | [optional] [default to 1] |
| **per_page** | **int**|  | [optional] [default to 50] |
| **endpoint** | **string**|  | [optional] |
| **integration_kind** | **string**|  | [optional] |
| **rejection_reason** | **string**|  | [optional] |
| **submitted_email** | **string**|  | [optional] |
| **was_false_positive** | **bool**|  | [optional] |

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

## `adminListPatternsApiV1AdminSpamPatternsGet()`

```php
adminListPatternsApiV1AdminSpamPatternsGet($page, $per_page, $is_active, $pattern_kind): mixed
```

Admin List Patterns

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\SpamAdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$page = 1; // int
$per_page = 50; // int
$is_active = True; // bool
$pattern_kind = 'pattern_kind_example'; // string

try {
    $result = $apiInstance->adminListPatternsApiV1AdminSpamPatternsGet($page, $per_page, $is_active, $pattern_kind);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling SpamAdminApi->adminListPatternsApiV1AdminSpamPatternsGet: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **page** | **int**|  | [optional] [default to 1] |
| **per_page** | **int**|  | [optional] [default to 50] |
| **is_active** | **bool**|  | [optional] |
| **pattern_kind** | **string**|  | [optional] |

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

## `adminMarkEventFalsePositiveApiV1AdminSpamEventsUuidMarkFalsePositivePost()`

```php
adminMarkEventFalsePositiveApiV1AdminSpamEventsUuidMarkFalsePositivePost($uuid): mixed
```

Admin Mark Event False Positive

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\SpamAdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $result = $apiInstance->adminMarkEventFalsePositiveApiV1AdminSpamEventsUuidMarkFalsePositivePost($uuid);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling SpamAdminApi->adminMarkEventFalsePositiveApiV1AdminSpamEventsUuidMarkFalsePositivePost: ', $e->getMessage(), PHP_EOL;
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

## `adminUpdatePatternApiV1AdminSpamPatternsUuidPut()`

```php
adminUpdatePatternApiV1AdminSpamPatternsUuidPut($uuid, $spam_pattern_update): mixed
```

Admin Update Pattern

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\SpamAdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string
$spam_pattern_update = new \ClientHub\Model\SpamPatternUpdate(); // \ClientHub\Model\SpamPatternUpdate

try {
    $result = $apiInstance->adminUpdatePatternApiV1AdminSpamPatternsUuidPut($uuid, $spam_pattern_update);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling SpamAdminApi->adminUpdatePatternApiV1AdminSpamPatternsUuidPut: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **uuid** | **string**|  | |
| **spam_pattern_update** | [**\ClientHub\Model\SpamPatternUpdate**](../Model/SpamPatternUpdate.md)|  | |

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
