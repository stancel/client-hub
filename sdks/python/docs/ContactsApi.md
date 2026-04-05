# clienthub.ContactsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**contact_summary_endpoint_api_v1_contacts_uuid_summary_get**](ContactsApi.md#contact_summary_endpoint_api_v1_contacts_uuid_summary_get) | **GET** /api/v1/contacts/{uuid}/summary | Contact Summary Endpoint
[**convert_contact_endpoint_api_v1_contacts_uuid_convert_post**](ContactsApi.md#convert_contact_endpoint_api_v1_contacts_uuid_convert_post) | **POST** /api/v1/contacts/{uuid}/convert | Convert Contact Endpoint
[**create_contact_endpoint_api_v1_contacts_post**](ContactsApi.md#create_contact_endpoint_api_v1_contacts_post) | **POST** /api/v1/contacts | Create Contact Endpoint
[**delete_contact_endpoint_api_v1_contacts_uuid_delete**](ContactsApi.md#delete_contact_endpoint_api_v1_contacts_uuid_delete) | **DELETE** /api/v1/contacts/{uuid} | Delete Contact Endpoint
[**delete_preference_api_v1_contacts_uuid_preferences_key_delete**](ContactsApi.md#delete_preference_api_v1_contacts_uuid_preferences_key_delete) | **DELETE** /api/v1/contacts/{uuid}/preferences/{key} | Delete Preference
[**get_contact_endpoint_api_v1_contacts_uuid_get**](ContactsApi.md#get_contact_endpoint_api_v1_contacts_uuid_get) | **GET** /api/v1/contacts/{uuid} | Get Contact Endpoint
[**get_marketing_optouts_api_v1_contacts_uuid_marketing_get**](ContactsApi.md#get_marketing_optouts_api_v1_contacts_uuid_marketing_get) | **GET** /api/v1/contacts/{uuid}/marketing | Get Marketing Optouts
[**list_contacts_endpoint_api_v1_contacts_get**](ContactsApi.md#list_contacts_endpoint_api_v1_contacts_get) | **GET** /api/v1/contacts | List Contacts Endpoint
[**list_preferences_api_v1_contacts_uuid_preferences_get**](ContactsApi.md#list_preferences_api_v1_contacts_uuid_preferences_get) | **GET** /api/v1/contacts/{uuid}/preferences | List Preferences
[**set_preference_api_v1_contacts_uuid_preferences_key_put**](ContactsApi.md#set_preference_api_v1_contacts_uuid_preferences_key_put) | **PUT** /api/v1/contacts/{uuid}/preferences/{key} | Set Preference
[**update_contact_endpoint_api_v1_contacts_uuid_put**](ContactsApi.md#update_contact_endpoint_api_v1_contacts_uuid_put) | **PUT** /api/v1/contacts/{uuid} | Update Contact Endpoint
[**update_marketing_optouts_api_v1_contacts_uuid_marketing_put**](ContactsApi.md#update_marketing_optouts_api_v1_contacts_uuid_marketing_put) | **PUT** /api/v1/contacts/{uuid}/marketing | Update Marketing Optouts


# **contact_summary_endpoint_api_v1_contacts_uuid_summary_get**
> object contact_summary_endpoint_api_v1_contacts_uuid_summary_get(uuid)

Contact Summary Endpoint

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
    api_instance = clienthub.ContactsApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Contact Summary Endpoint
        api_response = api_instance.contact_summary_endpoint_api_v1_contacts_uuid_summary_get(uuid)
        print("The response of ContactsApi->contact_summary_endpoint_api_v1_contacts_uuid_summary_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ContactsApi->contact_summary_endpoint_api_v1_contacts_uuid_summary_get: %s\n" % e)
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

# **convert_contact_endpoint_api_v1_contacts_uuid_convert_post**
> object convert_contact_endpoint_api_v1_contacts_uuid_convert_post(uuid)

Convert Contact Endpoint

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
    api_instance = clienthub.ContactsApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Convert Contact Endpoint
        api_response = api_instance.convert_contact_endpoint_api_v1_contacts_uuid_convert_post(uuid)
        print("The response of ContactsApi->convert_contact_endpoint_api_v1_contacts_uuid_convert_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ContactsApi->convert_contact_endpoint_api_v1_contacts_uuid_convert_post: %s\n" % e)
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

# **create_contact_endpoint_api_v1_contacts_post**
> object create_contact_endpoint_api_v1_contacts_post(contact_create)

Create Contact Endpoint

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.contact_create import ContactCreate
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
    api_instance = clienthub.ContactsApi(api_client)
    contact_create = clienthub.ContactCreate() # ContactCreate | 

    try:
        # Create Contact Endpoint
        api_response = api_instance.create_contact_endpoint_api_v1_contacts_post(contact_create)
        print("The response of ContactsApi->create_contact_endpoint_api_v1_contacts_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ContactsApi->create_contact_endpoint_api_v1_contacts_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **contact_create** | [**ContactCreate**](ContactCreate.md)|  | 

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

# **delete_contact_endpoint_api_v1_contacts_uuid_delete**
> delete_contact_endpoint_api_v1_contacts_uuid_delete(uuid)

Delete Contact Endpoint

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
    api_instance = clienthub.ContactsApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Delete Contact Endpoint
        api_instance.delete_contact_endpoint_api_v1_contacts_uuid_delete(uuid)
    except Exception as e:
        print("Exception when calling ContactsApi->delete_contact_endpoint_api_v1_contacts_uuid_delete: %s\n" % e)
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

# **delete_preference_api_v1_contacts_uuid_preferences_key_delete**
> delete_preference_api_v1_contacts_uuid_preferences_key_delete(uuid, key)

Delete Preference

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
    api_instance = clienthub.ContactsApi(api_client)
    uuid = 'uuid_example' # str | 
    key = 'key_example' # str | 

    try:
        # Delete Preference
        api_instance.delete_preference_api_v1_contacts_uuid_preferences_key_delete(uuid, key)
    except Exception as e:
        print("Exception when calling ContactsApi->delete_preference_api_v1_contacts_uuid_preferences_key_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **key** | **str**|  | 

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

# **get_contact_endpoint_api_v1_contacts_uuid_get**
> object get_contact_endpoint_api_v1_contacts_uuid_get(uuid)

Get Contact Endpoint

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
    api_instance = clienthub.ContactsApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Contact Endpoint
        api_response = api_instance.get_contact_endpoint_api_v1_contacts_uuid_get(uuid)
        print("The response of ContactsApi->get_contact_endpoint_api_v1_contacts_uuid_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ContactsApi->get_contact_endpoint_api_v1_contacts_uuid_get: %s\n" % e)
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

# **get_marketing_optouts_api_v1_contacts_uuid_marketing_get**
> object get_marketing_optouts_api_v1_contacts_uuid_marketing_get(uuid)

Get Marketing Optouts

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
    api_instance = clienthub.ContactsApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Marketing Optouts
        api_response = api_instance.get_marketing_optouts_api_v1_contacts_uuid_marketing_get(uuid)
        print("The response of ContactsApi->get_marketing_optouts_api_v1_contacts_uuid_marketing_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ContactsApi->get_marketing_optouts_api_v1_contacts_uuid_marketing_get: %s\n" % e)
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

# **list_contacts_endpoint_api_v1_contacts_get**
> object list_contacts_endpoint_api_v1_contacts_get(page=page, per_page=per_page, type=type, enrichment_status=enrichment_status, search=search, is_active=is_active, sort=sort, order=order)

List Contacts Endpoint

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
    api_instance = clienthub.ContactsApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    per_page = 25 # int |  (optional) (default to 25)
    type = 'type_example' # str |  (optional)
    enrichment_status = 'enrichment_status_example' # str |  (optional)
    search = 'search_example' # str |  (optional)
    is_active = True # bool |  (optional) (default to True)
    sort = 'last_name' # str |  (optional) (default to 'last_name')
    order = 'asc' # str |  (optional) (default to 'asc')

    try:
        # List Contacts Endpoint
        api_response = api_instance.list_contacts_endpoint_api_v1_contacts_get(page=page, per_page=per_page, type=type, enrichment_status=enrichment_status, search=search, is_active=is_active, sort=sort, order=order)
        print("The response of ContactsApi->list_contacts_endpoint_api_v1_contacts_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ContactsApi->list_contacts_endpoint_api_v1_contacts_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**|  | [optional] [default to 1]
 **per_page** | **int**|  | [optional] [default to 25]
 **type** | **str**|  | [optional] 
 **enrichment_status** | **str**|  | [optional] 
 **search** | **str**|  | [optional] 
 **is_active** | **bool**|  | [optional] [default to True]
 **sort** | **str**|  | [optional] [default to &#39;last_name&#39;]
 **order** | **str**|  | [optional] [default to &#39;asc&#39;]

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

# **list_preferences_api_v1_contacts_uuid_preferences_get**
> object list_preferences_api_v1_contacts_uuid_preferences_get(uuid)

List Preferences

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
    api_instance = clienthub.ContactsApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # List Preferences
        api_response = api_instance.list_preferences_api_v1_contacts_uuid_preferences_get(uuid)
        print("The response of ContactsApi->list_preferences_api_v1_contacts_uuid_preferences_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ContactsApi->list_preferences_api_v1_contacts_uuid_preferences_get: %s\n" % e)
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

# **set_preference_api_v1_contacts_uuid_preferences_key_put**
> object set_preference_api_v1_contacts_uuid_preferences_key_put(uuid, key, preference_set)

Set Preference

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.preference_set import PreferenceSet
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
    api_instance = clienthub.ContactsApi(api_client)
    uuid = 'uuid_example' # str | 
    key = 'key_example' # str | 
    preference_set = clienthub.PreferenceSet() # PreferenceSet | 

    try:
        # Set Preference
        api_response = api_instance.set_preference_api_v1_contacts_uuid_preferences_key_put(uuid, key, preference_set)
        print("The response of ContactsApi->set_preference_api_v1_contacts_uuid_preferences_key_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ContactsApi->set_preference_api_v1_contacts_uuid_preferences_key_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **key** | **str**|  | 
 **preference_set** | [**PreferenceSet**](PreferenceSet.md)|  | 

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

# **update_contact_endpoint_api_v1_contacts_uuid_put**
> object update_contact_endpoint_api_v1_contacts_uuid_put(uuid, contact_update)

Update Contact Endpoint

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.contact_update import ContactUpdate
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
    api_instance = clienthub.ContactsApi(api_client)
    uuid = 'uuid_example' # str | 
    contact_update = clienthub.ContactUpdate() # ContactUpdate | 

    try:
        # Update Contact Endpoint
        api_response = api_instance.update_contact_endpoint_api_v1_contacts_uuid_put(uuid, contact_update)
        print("The response of ContactsApi->update_contact_endpoint_api_v1_contacts_uuid_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ContactsApi->update_contact_endpoint_api_v1_contacts_uuid_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **contact_update** | [**ContactUpdate**](ContactUpdate.md)|  | 

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

# **update_marketing_optouts_api_v1_contacts_uuid_marketing_put**
> object update_marketing_optouts_api_v1_contacts_uuid_marketing_put(uuid, marketing_opt_outs)

Update Marketing Optouts

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.marketing_opt_outs import MarketingOptOuts
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
    api_instance = clienthub.ContactsApi(api_client)
    uuid = 'uuid_example' # str | 
    marketing_opt_outs = clienthub.MarketingOptOuts() # MarketingOptOuts | 

    try:
        # Update Marketing Optouts
        api_response = api_instance.update_marketing_optouts_api_v1_contacts_uuid_marketing_put(uuid, marketing_opt_outs)
        print("The response of ContactsApi->update_marketing_optouts_api_v1_contacts_uuid_marketing_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ContactsApi->update_marketing_optouts_api_v1_contacts_uuid_marketing_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **marketing_opt_outs** | [**MarketingOptOuts**](MarketingOptOuts.md)|  | 

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

