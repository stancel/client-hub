# ClientHub\LookupApi

All URIs are relative to http://localhost, except if the operation defines another base path.

| Method | HTTP request | Description |
| ------------- | ------------- | ------------- |
| [**lookupEmailApiV1LookupEmailEmailGet()**](LookupApi.md#lookupEmailApiV1LookupEmailEmailGet) | **GET** /api/v1/lookup/email/{email} | Lookup Email |
| [**lookupPhoneApiV1LookupPhoneNumberGet()**](LookupApi.md#lookupPhoneApiV1LookupPhoneNumberGet) | **GET** /api/v1/lookup/phone/{number} | Lookup Phone |


## `lookupEmailApiV1LookupEmailEmailGet()`

```php
lookupEmailApiV1LookupEmailEmailGet($email, $exact): mixed
```

Lookup Email

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\LookupApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$email = 'email_example'; // string
$exact = true; // bool

try {
    $result = $apiInstance->lookupEmailApiV1LookupEmailEmailGet($email, $exact);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling LookupApi->lookupEmailApiV1LookupEmailEmailGet: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **email** | **string**|  | |
| **exact** | **bool**|  | [optional] [default to true] |

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

## `lookupPhoneApiV1LookupPhoneNumberGet()`

```php
lookupPhoneApiV1LookupPhoneNumberGet($number, $exact): mixed
```

Lookup Phone

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\LookupApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$number = 'number_example'; // string
$exact = true; // bool

try {
    $result = $apiInstance->lookupPhoneApiV1LookupPhoneNumberGet($number, $exact);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling LookupApi->lookupPhoneApiV1LookupPhoneNumberGet: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **number** | **string**|  | |
| **exact** | **bool**|  | [optional] [default to true] |

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
