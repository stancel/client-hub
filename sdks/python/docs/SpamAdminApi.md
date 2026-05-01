# clienthub.SpamAdminApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**admin_create_pattern_api_v1_admin_spam_patterns_post**](SpamAdminApi.md#admin_create_pattern_api_v1_admin_spam_patterns_post) | **POST** /api/v1/admin/spam-patterns | Admin Create Pattern
[**admin_delete_pattern_api_v1_admin_spam_patterns_uuid_delete**](SpamAdminApi.md#admin_delete_pattern_api_v1_admin_spam_patterns_uuid_delete) | **DELETE** /api/v1/admin/spam-patterns/{uuid} | Admin Delete Pattern
[**admin_event_stats_api_v1_admin_spam_events_stats_get**](SpamAdminApi.md#admin_event_stats_api_v1_admin_spam_events_stats_get) | **GET** /api/v1/admin/spam-events/stats | Admin Event Stats
[**admin_list_events_api_v1_admin_spam_events_get**](SpamAdminApi.md#admin_list_events_api_v1_admin_spam_events_get) | **GET** /api/v1/admin/spam-events | Admin List Events
[**admin_list_patterns_api_v1_admin_spam_patterns_get**](SpamAdminApi.md#admin_list_patterns_api_v1_admin_spam_patterns_get) | **GET** /api/v1/admin/spam-patterns | Admin List Patterns
[**admin_mark_event_false_positive_api_v1_admin_spam_events_uuid_mark_false_positive_post**](SpamAdminApi.md#admin_mark_event_false_positive_api_v1_admin_spam_events_uuid_mark_false_positive_post) | **POST** /api/v1/admin/spam-events/{uuid}/mark-false-positive | Admin Mark Event False Positive
[**admin_update_pattern_api_v1_admin_spam_patterns_uuid_put**](SpamAdminApi.md#admin_update_pattern_api_v1_admin_spam_patterns_uuid_put) | **PUT** /api/v1/admin/spam-patterns/{uuid} | Admin Update Pattern


# **admin_create_pattern_api_v1_admin_spam_patterns_post**
> object admin_create_pattern_api_v1_admin_spam_patterns_post(spam_pattern_create)

Admin Create Pattern

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.spam_pattern_create import SpamPatternCreate
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
    api_instance = clienthub.SpamAdminApi(api_client)
    spam_pattern_create = clienthub.SpamPatternCreate() # SpamPatternCreate | 

    try:
        # Admin Create Pattern
        api_response = api_instance.admin_create_pattern_api_v1_admin_spam_patterns_post(spam_pattern_create)
        print("The response of SpamAdminApi->admin_create_pattern_api_v1_admin_spam_patterns_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SpamAdminApi->admin_create_pattern_api_v1_admin_spam_patterns_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **spam_pattern_create** | [**SpamPatternCreate**](SpamPatternCreate.md)|  | 

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

# **admin_delete_pattern_api_v1_admin_spam_patterns_uuid_delete**
> admin_delete_pattern_api_v1_admin_spam_patterns_uuid_delete(uuid)

Admin Delete Pattern

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
    api_instance = clienthub.SpamAdminApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Admin Delete Pattern
        api_instance.admin_delete_pattern_api_v1_admin_spam_patterns_uuid_delete(uuid)
    except Exception as e:
        print("Exception when calling SpamAdminApi->admin_delete_pattern_api_v1_admin_spam_patterns_uuid_delete: %s\n" % e)
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

# **admin_event_stats_api_v1_admin_spam_events_stats_get**
> object admin_event_stats_api_v1_admin_spam_events_stats_get()

Admin Event Stats

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
    api_instance = clienthub.SpamAdminApi(api_client)

    try:
        # Admin Event Stats
        api_response = api_instance.admin_event_stats_api_v1_admin_spam_events_stats_get()
        print("The response of SpamAdminApi->admin_event_stats_api_v1_admin_spam_events_stats_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SpamAdminApi->admin_event_stats_api_v1_admin_spam_events_stats_get: %s\n" % e)
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

# **admin_list_events_api_v1_admin_spam_events_get**
> object admin_list_events_api_v1_admin_spam_events_get(page=page, per_page=per_page, endpoint=endpoint, integration_kind=integration_kind, rejection_reason=rejection_reason, submitted_email=submitted_email, was_false_positive=was_false_positive)

Admin List Events

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
    api_instance = clienthub.SpamAdminApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    per_page = 50 # int |  (optional) (default to 50)
    endpoint = 'endpoint_example' # str |  (optional)
    integration_kind = 'integration_kind_example' # str |  (optional)
    rejection_reason = 'rejection_reason_example' # str |  (optional)
    submitted_email = 'submitted_email_example' # str |  (optional)
    was_false_positive = True # bool |  (optional)

    try:
        # Admin List Events
        api_response = api_instance.admin_list_events_api_v1_admin_spam_events_get(page=page, per_page=per_page, endpoint=endpoint, integration_kind=integration_kind, rejection_reason=rejection_reason, submitted_email=submitted_email, was_false_positive=was_false_positive)
        print("The response of SpamAdminApi->admin_list_events_api_v1_admin_spam_events_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SpamAdminApi->admin_list_events_api_v1_admin_spam_events_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**|  | [optional] [default to 1]
 **per_page** | **int**|  | [optional] [default to 50]
 **endpoint** | **str**|  | [optional] 
 **integration_kind** | **str**|  | [optional] 
 **rejection_reason** | **str**|  | [optional] 
 **submitted_email** | **str**|  | [optional] 
 **was_false_positive** | **bool**|  | [optional] 

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

# **admin_list_patterns_api_v1_admin_spam_patterns_get**
> object admin_list_patterns_api_v1_admin_spam_patterns_get(page=page, per_page=per_page, is_active=is_active, pattern_kind=pattern_kind)

Admin List Patterns

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
    api_instance = clienthub.SpamAdminApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    per_page = 50 # int |  (optional) (default to 50)
    is_active = True # bool |  (optional)
    pattern_kind = 'pattern_kind_example' # str |  (optional)

    try:
        # Admin List Patterns
        api_response = api_instance.admin_list_patterns_api_v1_admin_spam_patterns_get(page=page, per_page=per_page, is_active=is_active, pattern_kind=pattern_kind)
        print("The response of SpamAdminApi->admin_list_patterns_api_v1_admin_spam_patterns_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SpamAdminApi->admin_list_patterns_api_v1_admin_spam_patterns_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**|  | [optional] [default to 1]
 **per_page** | **int**|  | [optional] [default to 50]
 **is_active** | **bool**|  | [optional] 
 **pattern_kind** | **str**|  | [optional] 

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

# **admin_mark_event_false_positive_api_v1_admin_spam_events_uuid_mark_false_positive_post**
> object admin_mark_event_false_positive_api_v1_admin_spam_events_uuid_mark_false_positive_post(uuid)

Admin Mark Event False Positive

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
    api_instance = clienthub.SpamAdminApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Admin Mark Event False Positive
        api_response = api_instance.admin_mark_event_false_positive_api_v1_admin_spam_events_uuid_mark_false_positive_post(uuid)
        print("The response of SpamAdminApi->admin_mark_event_false_positive_api_v1_admin_spam_events_uuid_mark_false_positive_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SpamAdminApi->admin_mark_event_false_positive_api_v1_admin_spam_events_uuid_mark_false_positive_post: %s\n" % e)
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

# **admin_update_pattern_api_v1_admin_spam_patterns_uuid_put**
> object admin_update_pattern_api_v1_admin_spam_patterns_uuid_put(uuid, spam_pattern_update)

Admin Update Pattern

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.spam_pattern_update import SpamPatternUpdate
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
    api_instance = clienthub.SpamAdminApi(api_client)
    uuid = 'uuid_example' # str | 
    spam_pattern_update = clienthub.SpamPatternUpdate() # SpamPatternUpdate | 

    try:
        # Admin Update Pattern
        api_response = api_instance.admin_update_pattern_api_v1_admin_spam_patterns_uuid_put(uuid, spam_pattern_update)
        print("The response of SpamAdminApi->admin_update_pattern_api_v1_admin_spam_patterns_uuid_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SpamAdminApi->admin_update_pattern_api_v1_admin_spam_patterns_uuid_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **spam_pattern_update** | [**SpamPatternUpdate**](SpamPatternUpdate.md)|  | 

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

