# ClientHub\ContactsApi

All URIs are relative to http://localhost, except if the operation defines another base path.

| Method | HTTP request | Description |
| ------------- | ------------- | ------------- |
| [**contactSummaryEndpointApiV1ContactsUuidSummaryGet()**](ContactsApi.md#contactSummaryEndpointApiV1ContactsUuidSummaryGet) | **GET** /api/v1/contacts/{uuid}/summary | Contact Summary Endpoint |
| [**convertContactEndpointApiV1ContactsUuidConvertPost()**](ContactsApi.md#convertContactEndpointApiV1ContactsUuidConvertPost) | **POST** /api/v1/contacts/{uuid}/convert | Convert Contact Endpoint |
| [**createContactEndpointApiV1ContactsPost()**](ContactsApi.md#createContactEndpointApiV1ContactsPost) | **POST** /api/v1/contacts | Create Contact Endpoint |
| [**deleteContactEndpointApiV1ContactsUuidDelete()**](ContactsApi.md#deleteContactEndpointApiV1ContactsUuidDelete) | **DELETE** /api/v1/contacts/{uuid} | Delete Contact Endpoint |
| [**deletePreferenceApiV1ContactsUuidPreferencesKeyDelete()**](ContactsApi.md#deletePreferenceApiV1ContactsUuidPreferencesKeyDelete) | **DELETE** /api/v1/contacts/{uuid}/preferences/{key} | Delete Preference |
| [**getContactEndpointApiV1ContactsUuidGet()**](ContactsApi.md#getContactEndpointApiV1ContactsUuidGet) | **GET** /api/v1/contacts/{uuid} | Get Contact Endpoint |
| [**getMarketingOptoutsApiV1ContactsUuidMarketingGet()**](ContactsApi.md#getMarketingOptoutsApiV1ContactsUuidMarketingGet) | **GET** /api/v1/contacts/{uuid}/marketing | Get Marketing Optouts |
| [**listContactsEndpointApiV1ContactsGet()**](ContactsApi.md#listContactsEndpointApiV1ContactsGet) | **GET** /api/v1/contacts | List Contacts Endpoint |
| [**listPreferencesApiV1ContactsUuidPreferencesGet()**](ContactsApi.md#listPreferencesApiV1ContactsUuidPreferencesGet) | **GET** /api/v1/contacts/{uuid}/preferences | List Preferences |
| [**setPreferenceApiV1ContactsUuidPreferencesKeyPut()**](ContactsApi.md#setPreferenceApiV1ContactsUuidPreferencesKeyPut) | **PUT** /api/v1/contacts/{uuid}/preferences/{key} | Set Preference |
| [**updateContactEndpointApiV1ContactsUuidPut()**](ContactsApi.md#updateContactEndpointApiV1ContactsUuidPut) | **PUT** /api/v1/contacts/{uuid} | Update Contact Endpoint |
| [**updateMarketingOptoutsApiV1ContactsUuidMarketingPut()**](ContactsApi.md#updateMarketingOptoutsApiV1ContactsUuidMarketingPut) | **PUT** /api/v1/contacts/{uuid}/marketing | Update Marketing Optouts |


## `contactSummaryEndpointApiV1ContactsUuidSummaryGet()`

```php
contactSummaryEndpointApiV1ContactsUuidSummaryGet($uuid): mixed
```

Contact Summary Endpoint

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\ContactsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $result = $apiInstance->contactSummaryEndpointApiV1ContactsUuidSummaryGet($uuid);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling ContactsApi->contactSummaryEndpointApiV1ContactsUuidSummaryGet: ', $e->getMessage(), PHP_EOL;
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

## `convertContactEndpointApiV1ContactsUuidConvertPost()`

```php
convertContactEndpointApiV1ContactsUuidConvertPost($uuid): mixed
```

Convert Contact Endpoint

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\ContactsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $result = $apiInstance->convertContactEndpointApiV1ContactsUuidConvertPost($uuid);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling ContactsApi->convertContactEndpointApiV1ContactsUuidConvertPost: ', $e->getMessage(), PHP_EOL;
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

## `createContactEndpointApiV1ContactsPost()`

```php
createContactEndpointApiV1ContactsPost($contact_create): mixed
```

Create Contact Endpoint

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\ContactsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$contact_create = new \ClientHub\Model\ContactCreate(); // \ClientHub\Model\ContactCreate

try {
    $result = $apiInstance->createContactEndpointApiV1ContactsPost($contact_create);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling ContactsApi->createContactEndpointApiV1ContactsPost: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **contact_create** | [**\ClientHub\Model\ContactCreate**](../Model/ContactCreate.md)|  | |

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

## `deleteContactEndpointApiV1ContactsUuidDelete()`

```php
deleteContactEndpointApiV1ContactsUuidDelete($uuid)
```

Delete Contact Endpoint

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\ContactsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $apiInstance->deleteContactEndpointApiV1ContactsUuidDelete($uuid);
} catch (Exception $e) {
    echo 'Exception when calling ContactsApi->deleteContactEndpointApiV1ContactsUuidDelete: ', $e->getMessage(), PHP_EOL;
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

## `deletePreferenceApiV1ContactsUuidPreferencesKeyDelete()`

```php
deletePreferenceApiV1ContactsUuidPreferencesKeyDelete($uuid, $key)
```

Delete Preference

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\ContactsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string
$key = 'key_example'; // string

try {
    $apiInstance->deletePreferenceApiV1ContactsUuidPreferencesKeyDelete($uuid, $key);
} catch (Exception $e) {
    echo 'Exception when calling ContactsApi->deletePreferenceApiV1ContactsUuidPreferencesKeyDelete: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **uuid** | **string**|  | |
| **key** | **string**|  | |

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

## `getContactEndpointApiV1ContactsUuidGet()`

```php
getContactEndpointApiV1ContactsUuidGet($uuid): mixed
```

Get Contact Endpoint

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\ContactsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $result = $apiInstance->getContactEndpointApiV1ContactsUuidGet($uuid);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling ContactsApi->getContactEndpointApiV1ContactsUuidGet: ', $e->getMessage(), PHP_EOL;
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

## `getMarketingOptoutsApiV1ContactsUuidMarketingGet()`

```php
getMarketingOptoutsApiV1ContactsUuidMarketingGet($uuid): mixed
```

Get Marketing Optouts

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\ContactsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $result = $apiInstance->getMarketingOptoutsApiV1ContactsUuidMarketingGet($uuid);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling ContactsApi->getMarketingOptoutsApiV1ContactsUuidMarketingGet: ', $e->getMessage(), PHP_EOL;
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

## `listContactsEndpointApiV1ContactsGet()`

```php
listContactsEndpointApiV1ContactsGet($page, $per_page, $type, $enrichment_status, $search, $is_active, $sort, $order): mixed
```

List Contacts Endpoint

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\ContactsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$page = 1; // int
$per_page = 25; // int
$type = 'type_example'; // string
$enrichment_status = 'enrichment_status_example'; // string
$search = 'search_example'; // string
$is_active = true; // bool
$sort = 'last_name'; // string
$order = 'asc'; // string

try {
    $result = $apiInstance->listContactsEndpointApiV1ContactsGet($page, $per_page, $type, $enrichment_status, $search, $is_active, $sort, $order);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling ContactsApi->listContactsEndpointApiV1ContactsGet: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **page** | **int**|  | [optional] [default to 1] |
| **per_page** | **int**|  | [optional] [default to 25] |
| **type** | **string**|  | [optional] |
| **enrichment_status** | **string**|  | [optional] |
| **search** | **string**|  | [optional] |
| **is_active** | **bool**|  | [optional] [default to true] |
| **sort** | **string**|  | [optional] [default to &#39;last_name&#39;] |
| **order** | **string**|  | [optional] [default to &#39;asc&#39;] |

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

## `listPreferencesApiV1ContactsUuidPreferencesGet()`

```php
listPreferencesApiV1ContactsUuidPreferencesGet($uuid): mixed
```

List Preferences

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\ContactsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string

try {
    $result = $apiInstance->listPreferencesApiV1ContactsUuidPreferencesGet($uuid);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling ContactsApi->listPreferencesApiV1ContactsUuidPreferencesGet: ', $e->getMessage(), PHP_EOL;
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

## `setPreferenceApiV1ContactsUuidPreferencesKeyPut()`

```php
setPreferenceApiV1ContactsUuidPreferencesKeyPut($uuid, $key, $preference_set): mixed
```

Set Preference

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\ContactsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string
$key = 'key_example'; // string
$preference_set = new \ClientHub\Model\PreferenceSet(); // \ClientHub\Model\PreferenceSet

try {
    $result = $apiInstance->setPreferenceApiV1ContactsUuidPreferencesKeyPut($uuid, $key, $preference_set);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling ContactsApi->setPreferenceApiV1ContactsUuidPreferencesKeyPut: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **uuid** | **string**|  | |
| **key** | **string**|  | |
| **preference_set** | [**\ClientHub\Model\PreferenceSet**](../Model/PreferenceSet.md)|  | |

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

## `updateContactEndpointApiV1ContactsUuidPut()`

```php
updateContactEndpointApiV1ContactsUuidPut($uuid, $contact_update): mixed
```

Update Contact Endpoint

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\ContactsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string
$contact_update = new \ClientHub\Model\ContactUpdate(); // \ClientHub\Model\ContactUpdate

try {
    $result = $apiInstance->updateContactEndpointApiV1ContactsUuidPut($uuid, $contact_update);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling ContactsApi->updateContactEndpointApiV1ContactsUuidPut: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **uuid** | **string**|  | |
| **contact_update** | [**\ClientHub\Model\ContactUpdate**](../Model/ContactUpdate.md)|  | |

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

## `updateMarketingOptoutsApiV1ContactsUuidMarketingPut()`

```php
updateMarketingOptoutsApiV1ContactsUuidMarketingPut($uuid, $marketing_opt_outs): mixed
```

Update Marketing Optouts

### Example

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');


// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\ContactsApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string
$marketing_opt_outs = new \ClientHub\Model\MarketingOptOuts(); // \ClientHub\Model\MarketingOptOuts

try {
    $result = $apiInstance->updateMarketingOptoutsApiV1ContactsUuidMarketingPut($uuid, $marketing_opt_outs);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling ContactsApi->updateMarketingOptoutsApiV1ContactsUuidMarketingPut: ', $e->getMessage(), PHP_EOL;
}
```

### Parameters

| Name | Type | Description  | Notes |
| ------------- | ------------- | ------------- | ------------- |
| **uuid** | **string**|  | |
| **marketing_opt_outs** | [**\ClientHub\Model\MarketingOptOuts**](../Model/MarketingOptOuts.md)|  | |

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
