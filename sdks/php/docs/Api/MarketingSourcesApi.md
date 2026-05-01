# ClientHub\MarketingSourcesApi

All URIs are relative to http://localhost, except if the operation defines another base path.

| Method | HTTP request | Description |
| ------------- | ------------- | ------------- |
| [**getActiveMarketingSourcesApiV1MarketingSourcesGet()**](MarketingSourcesApi.md#getActiveMarketingSourcesApiV1MarketingSourcesGet) | **GET** /api/v1/marketing-sources | Get Active Marketing Sources |


## `getActiveMarketingSourcesApiV1MarketingSourcesGet()`

```php
getActiveMarketingSourcesApiV1MarketingSourcesGet(): mixed
```

Get Active Marketing Sources

Return ``[{\"code\": ..., \"label\": ...}, ...]`` for active rows.

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\MarketingSourcesApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);

try {
    $result = $apiInstance->getActiveMarketingSourcesApiV1MarketingSourcesGet();
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling MarketingSourcesApi->getActiveMarketingSourcesApiV1MarketingSourcesGet: ', $e->getMessage(), PHP_EOL;
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
