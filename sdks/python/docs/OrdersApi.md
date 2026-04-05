# clienthub.OrdersApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**change_order_status_api_v1_orders_uuid_status_post**](OrdersApi.md#change_order_status_api_v1_orders_uuid_status_post) | **POST** /api/v1/orders/{uuid}/status | Change Order Status
[**create_order_api_v1_orders_post**](OrdersApi.md#create_order_api_v1_orders_post) | **POST** /api/v1/orders | Create Order
[**delete_order_api_v1_orders_uuid_delete**](OrdersApi.md#delete_order_api_v1_orders_uuid_delete) | **DELETE** /api/v1/orders/{uuid} | Delete Order
[**get_order_api_v1_orders_uuid_get**](OrdersApi.md#get_order_api_v1_orders_uuid_get) | **GET** /api/v1/orders/{uuid} | Get Order
[**list_orders_api_v1_orders_get**](OrdersApi.md#list_orders_api_v1_orders_get) | **GET** /api/v1/orders | List Orders


# **change_order_status_api_v1_orders_uuid_status_post**
> object change_order_status_api_v1_orders_uuid_status_post(uuid, status_change)

Change Order Status

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.status_change import StatusChange
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
    api_instance = clienthub.OrdersApi(api_client)
    uuid = 'uuid_example' # str | 
    status_change = clienthub.StatusChange() # StatusChange | 

    try:
        # Change Order Status
        api_response = api_instance.change_order_status_api_v1_orders_uuid_status_post(uuid, status_change)
        print("The response of OrdersApi->change_order_status_api_v1_orders_uuid_status_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->change_order_status_api_v1_orders_uuid_status_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **status_change** | [**StatusChange**](StatusChange.md)|  | 

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

# **create_order_api_v1_orders_post**
> object create_order_api_v1_orders_post(order_create)

Create Order

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.order_create import OrderCreate
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
    api_instance = clienthub.OrdersApi(api_client)
    order_create = clienthub.OrderCreate() # OrderCreate | 

    try:
        # Create Order
        api_response = api_instance.create_order_api_v1_orders_post(order_create)
        print("The response of OrdersApi->create_order_api_v1_orders_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->create_order_api_v1_orders_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_create** | [**OrderCreate**](OrderCreate.md)|  | 

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

# **delete_order_api_v1_orders_uuid_delete**
> delete_order_api_v1_orders_uuid_delete(uuid)

Delete Order

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
    api_instance = clienthub.OrdersApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Delete Order
        api_instance.delete_order_api_v1_orders_uuid_delete(uuid)
    except Exception as e:
        print("Exception when calling OrdersApi->delete_order_api_v1_orders_uuid_delete: %s\n" % e)
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

# **get_order_api_v1_orders_uuid_get**
> object get_order_api_v1_orders_uuid_get(uuid)

Get Order

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
    api_instance = clienthub.OrdersApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Order
        api_response = api_instance.get_order_api_v1_orders_uuid_get(uuid)
        print("The response of OrdersApi->get_order_api_v1_orders_uuid_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->get_order_api_v1_orders_uuid_get: %s\n" % e)
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

# **list_orders_api_v1_orders_get**
> object list_orders_api_v1_orders_get(page=page, per_page=per_page, status=status, contact_uuid=contact_uuid)

List Orders

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
    api_instance = clienthub.OrdersApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    per_page = 25 # int |  (optional) (default to 25)
    status = 'status_example' # str |  (optional)
    contact_uuid = 'contact_uuid_example' # str |  (optional)

    try:
        # List Orders
        api_response = api_instance.list_orders_api_v1_orders_get(page=page, per_page=per_page, status=status, contact_uuid=contact_uuid)
        print("The response of OrdersApi->list_orders_api_v1_orders_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->list_orders_api_v1_orders_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**|  | [optional] [default to 1]
 **per_page** | **int**|  | [optional] [default to 25]
 **status** | **str**|  | [optional] 
 **contact_uuid** | **str**|  | [optional] 

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

