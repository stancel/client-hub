# clienthub.AdminApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_api_key_api_v1_admin_sources_uuid_api_keys_post**](AdminApi.md#create_api_key_api_v1_admin_sources_uuid_api_keys_post) | **POST** /api/v1/admin/sources/{uuid}/api-keys | Create Api Key
[**create_source_api_v1_admin_sources_post**](AdminApi.md#create_source_api_v1_admin_sources_post) | **POST** /api/v1/admin/sources | Create Source
[**delete_source_api_v1_admin_sources_uuid_delete**](AdminApi.md#delete_source_api_v1_admin_sources_uuid_delete) | **DELETE** /api/v1/admin/sources/{uuid} | Delete Source
[**get_source_api_v1_admin_sources_uuid_get**](AdminApi.md#get_source_api_v1_admin_sources_uuid_get) | **GET** /api/v1/admin/sources/{uuid} | Get Source
[**list_api_keys_api_v1_admin_sources_uuid_api_keys_get**](AdminApi.md#list_api_keys_api_v1_admin_sources_uuid_api_keys_get) | **GET** /api/v1/admin/sources/{uuid}/api-keys | List Api Keys
[**list_events_api_v1_admin_events_get**](AdminApi.md#list_events_api_v1_admin_events_get) | **GET** /api/v1/admin/events | List Events
[**list_sources_api_v1_admin_sources_get**](AdminApi.md#list_sources_api_v1_admin_sources_get) | **GET** /api/v1/admin/sources | List Sources
[**revoke_api_key_api_v1_admin_api_keys_uuid_delete**](AdminApi.md#revoke_api_key_api_v1_admin_api_keys_uuid_delete) | **DELETE** /api/v1/admin/api-keys/{uuid} | Revoke Api Key
[**update_source_api_v1_admin_sources_uuid_put**](AdminApi.md#update_source_api_v1_admin_sources_uuid_put) | **PUT** /api/v1/admin/sources/{uuid} | Update Source


# **create_api_key_api_v1_admin_sources_uuid_api_keys_post**
> object create_api_key_api_v1_admin_sources_uuid_api_keys_post(uuid, api_key_create)

Create Api Key

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.api_key_create import ApiKeyCreate
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
    api_instance = clienthub.AdminApi(api_client)
    uuid = 'uuid_example' # str | 
    api_key_create = clienthub.ApiKeyCreate() # ApiKeyCreate | 

    try:
        # Create Api Key
        api_response = api_instance.create_api_key_api_v1_admin_sources_uuid_api_keys_post(uuid, api_key_create)
        print("The response of AdminApi->create_api_key_api_v1_admin_sources_uuid_api_keys_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->create_api_key_api_v1_admin_sources_uuid_api_keys_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **api_key_create** | [**ApiKeyCreate**](ApiKeyCreate.md)|  | 

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
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_source_api_v1_admin_sources_post**
> object create_source_api_v1_admin_sources_post(source_create)

Create Source

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.source_create import SourceCreate
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
    api_instance = clienthub.AdminApi(api_client)
    source_create = clienthub.SourceCreate() # SourceCreate | 

    try:
        # Create Source
        api_response = api_instance.create_source_api_v1_admin_sources_post(source_create)
        print("The response of AdminApi->create_source_api_v1_admin_sources_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->create_source_api_v1_admin_sources_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_create** | [**SourceCreate**](SourceCreate.md)|  | 

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
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_source_api_v1_admin_sources_uuid_delete**
> delete_source_api_v1_admin_sources_uuid_delete(uuid)

Delete Source

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
    api_instance = clienthub.AdminApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Delete Source
        api_instance.delete_source_api_v1_admin_sources_uuid_delete(uuid)
    except Exception as e:
        print("Exception when calling AdminApi->delete_source_api_v1_admin_sources_uuid_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_source_api_v1_admin_sources_uuid_get**
> object get_source_api_v1_admin_sources_uuid_get(uuid)

Get Source

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
    api_instance = clienthub.AdminApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Source
        api_response = api_instance.get_source_api_v1_admin_sources_uuid_get(uuid)
        print("The response of AdminApi->get_source_api_v1_admin_sources_uuid_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->get_source_api_v1_admin_sources_uuid_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_api_keys_api_v1_admin_sources_uuid_api_keys_get**
> object list_api_keys_api_v1_admin_sources_uuid_api_keys_get(uuid)

List Api Keys

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
    api_instance = clienthub.AdminApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # List Api Keys
        api_response = api_instance.list_api_keys_api_v1_admin_sources_uuid_api_keys_get(uuid)
        print("The response of AdminApi->list_api_keys_api_v1_admin_sources_uuid_api_keys_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->list_api_keys_api_v1_admin_sources_uuid_api_keys_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_events_api_v1_admin_events_get**
> object list_events_api_v1_admin_events_get(source_code=source_code, channel_code=channel_code, date_from=date_from, date_to=date_to, limit=limit)

List Events

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
    api_instance = clienthub.AdminApi(api_client)
    source_code = 'source_code_example' # str |  (optional)
    channel_code = 'channel_code_example' # str |  (optional)
    date_from = 'date_from_example' # str |  (optional)
    date_to = 'date_to_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)

    try:
        # List Events
        api_response = api_instance.list_events_api_v1_admin_events_get(source_code=source_code, channel_code=channel_code, date_from=date_from, date_to=date_to, limit=limit)
        print("The response of AdminApi->list_events_api_v1_admin_events_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->list_events_api_v1_admin_events_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **source_code** | **str**|  | [optional] 
 **channel_code** | **str**|  | [optional] 
 **date_from** | **str**|  | [optional] 
 **date_to** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 100]

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_sources_api_v1_admin_sources_get**
> object list_sources_api_v1_admin_sources_get()

List Sources

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
    api_instance = clienthub.AdminApi(api_client)

    try:
        # List Sources
        api_response = api_instance.list_sources_api_v1_admin_sources_get()
        print("The response of AdminApi->list_sources_api_v1_admin_sources_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->list_sources_api_v1_admin_sources_get: %s\n" % e)
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

# **revoke_api_key_api_v1_admin_api_keys_uuid_delete**
> revoke_api_key_api_v1_admin_api_keys_uuid_delete(uuid)

Revoke Api Key

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
    api_instance = clienthub.AdminApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Revoke Api Key
        api_instance.revoke_api_key_api_v1_admin_api_keys_uuid_delete(uuid)
    except Exception as e:
        print("Exception when calling AdminApi->revoke_api_key_api_v1_admin_api_keys_uuid_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_source_api_v1_admin_sources_uuid_put**
> object update_source_api_v1_admin_sources_uuid_put(uuid, source_update)

Update Source

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.source_update import SourceUpdate
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
    api_instance = clienthub.AdminApi(api_client)
    uuid = 'uuid_example' # str | 
    source_update = clienthub.SourceUpdate() # SourceUpdate | 

    try:
        # Update Source
        api_response = api_instance.update_source_api_v1_admin_sources_uuid_put(uuid, source_update)
        print("The response of AdminApi->update_source_api_v1_admin_sources_uuid_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->update_source_api_v1_admin_sources_uuid_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **source_update** | [**SourceUpdate**](SourceUpdate.md)|  | 

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

