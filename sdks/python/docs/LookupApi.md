# clienthub.LookupApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**lookup_email_api_v1_lookup_email_email_get**](LookupApi.md#lookup_email_api_v1_lookup_email_email_get) | **GET** /api/v1/lookup/email/{email} | Lookup Email
[**lookup_phone_api_v1_lookup_phone_number_get**](LookupApi.md#lookup_phone_api_v1_lookup_phone_number_get) | **GET** /api/v1/lookup/phone/{number} | Lookup Phone


# **lookup_email_api_v1_lookup_email_email_get**
> object lookup_email_api_v1_lookup_email_email_get(email, exact=exact)

Lookup Email

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
    api_instance = clienthub.LookupApi(api_client)
    email = 'email_example' # str | 
    exact = True # bool |  (optional) (default to True)

    try:
        # Lookup Email
        api_response = api_instance.lookup_email_api_v1_lookup_email_email_get(email, exact=exact)
        print("The response of LookupApi->lookup_email_api_v1_lookup_email_email_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LookupApi->lookup_email_api_v1_lookup_email_email_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **email** | **str**|  | 
 **exact** | **bool**|  | [optional] [default to True]

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

# **lookup_phone_api_v1_lookup_phone_number_get**
> object lookup_phone_api_v1_lookup_phone_number_get(number, exact=exact)

Lookup Phone

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
    api_instance = clienthub.LookupApi(api_client)
    number = 'number_example' # str | 
    exact = True # bool |  (optional) (default to True)

    try:
        # Lookup Phone
        api_response = api_instance.lookup_phone_api_v1_lookup_phone_number_get(number, exact=exact)
        print("The response of LookupApi->lookup_phone_api_v1_lookup_phone_number_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LookupApi->lookup_phone_api_v1_lookup_phone_number_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **number** | **str**|  | 
 **exact** | **bool**|  | [optional] [default to True]

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

