# ClientHub\SpamPatternsApi

All URIs are relative to http://localhost, except if the operation defines another base path.

| Method | HTTP request | Description |
| ------------- | ------------- | ------------- |
| [**getActivePatternsPublicApiV1SpamPatternsGet()**](SpamPatternsApi.md#getActivePatternsPublicApiV1SpamPatternsGet) | **GET** /api/v1/spam-patterns | Get Active Patterns Public |


## `getActivePatternsPublicApiV1SpamPatternsGet()`

```php
getActivePatternsPublicApiV1SpamPatternsGet(): mixed
```

Get Active Patterns Public

Return active patterns grouped by kind. Consumer sites fetch this at build/deploy time to keep their server-side filter in sync with Client Hub's canonical list.

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\SpamPatternsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);

try {
    $result = $apiInstance->getActivePatternsPublicApiV1SpamPatternsGet();
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling SpamPatternsApi->getActivePatternsPublicApiV1SpamPatternsGet: ', $e->getMessage(), PHP_EOL;
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
