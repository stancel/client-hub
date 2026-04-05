# clienthub.SettingsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_settings_api_v1_settings_get**](SettingsApi.md#get_settings_api_v1_settings_get) | **GET** /api/v1/settings | Get Settings
[**update_settings_api_v1_settings_put**](SettingsApi.md#update_settings_api_v1_settings_put) | **PUT** /api/v1/settings | Update Settings


# **get_settings_api_v1_settings_get**
> object get_settings_api_v1_settings_get()

Get Settings

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = clienthub.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKeyHeader
configuration.api_key['APIKeyHeader'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKeyHeader'] = 'Bearer'

# Enter a context with an instance of the API client
with clienthub.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = clienthub.SettingsApi(api_client)

    try:
        # Get Settings
        api_response = api_instance.get_settings_api_v1_settings_get()
        print("The response of SettingsApi->get_settings_api_v1_settings_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SettingsApi->get_settings_api_v1_settings_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_settings_api_v1_settings_put**
> object update_settings_api_v1_settings_put(settings_update)

Update Settings

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.settings_update import SettingsUpdate
from clienthub.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = clienthub.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKeyHeader
configuration.api_key['APIKeyHeader'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKeyHeader'] = 'Bearer'

# Enter a context with an instance of the API client
with clienthub.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = clienthub.SettingsApi(api_client)
    settings_update = clienthub.SettingsUpdate() # SettingsUpdate | 

    try:
        # Update Settings
        api_response = api_instance.update_settings_api_v1_settings_put(settings_update)
        print("The response of SettingsApi->update_settings_api_v1_settings_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SettingsApi->update_settings_api_v1_settings_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **settings_update** | [**SettingsUpdate**](SettingsUpdate.md)|  | 

### Return type

**object**

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

