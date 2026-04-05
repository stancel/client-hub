# clienthub.CommunicationsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_communication_api_v1_communications_post**](CommunicationsApi.md#create_communication_api_v1_communications_post) | **POST** /api/v1/communications | Create Communication
[**get_communication_api_v1_communications_uuid_get**](CommunicationsApi.md#get_communication_api_v1_communications_uuid_get) | **GET** /api/v1/communications/{uuid} | Get Communication
[**list_communications_api_v1_communications_get**](CommunicationsApi.md#list_communications_api_v1_communications_get) | **GET** /api/v1/communications | List Communications


# **create_communication_api_v1_communications_post**
> object create_communication_api_v1_communications_post(comm_create)

Create Communication

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.comm_create import CommCreate
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
    api_instance = clienthub.CommunicationsApi(api_client)
    comm_create = clienthub.CommCreate() # CommCreate | 

    try:
        # Create Communication
        api_response = api_instance.create_communication_api_v1_communications_post(comm_create)
        print("The response of CommunicationsApi->create_communication_api_v1_communications_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommunicationsApi->create_communication_api_v1_communications_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **comm_create** | [**CommCreate**](CommCreate.md)|  | 

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

# **get_communication_api_v1_communications_uuid_get**
> object get_communication_api_v1_communications_uuid_get(uuid)

Get Communication

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
    api_instance = clienthub.CommunicationsApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Communication
        api_response = api_instance.get_communication_api_v1_communications_uuid_get(uuid)
        print("The response of CommunicationsApi->get_communication_api_v1_communications_uuid_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommunicationsApi->get_communication_api_v1_communications_uuid_get: %s\n" % e)
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

# **list_communications_api_v1_communications_get**
> object list_communications_api_v1_communications_get(page=page, per_page=per_page, contact_uuid=contact_uuid, channel=channel, direction=direction)

List Communications

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
    api_instance = clienthub.CommunicationsApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    per_page = 25 # int |  (optional) (default to 25)
    contact_uuid = 'contact_uuid_example' # str |  (optional)
    channel = 'channel_example' # str |  (optional)
    direction = 'direction_example' # str |  (optional)

    try:
        # List Communications
        api_response = api_instance.list_communications_api_v1_communications_get(page=page, per_page=per_page, contact_uuid=contact_uuid, channel=channel, direction=direction)
        print("The response of CommunicationsApi->list_communications_api_v1_communications_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CommunicationsApi->list_communications_api_v1_communications_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**|  | [optional] [default to 1]
 **per_page** | **int**|  | [optional] [default to 25]
 **contact_uuid** | **str**|  | [optional] 
 **channel** | **str**|  | [optional] 
 **direction** | **str**|  | [optional] 

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

