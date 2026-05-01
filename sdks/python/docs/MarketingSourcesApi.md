# clienthub.MarketingSourcesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_active_marketing_sources_api_v1_marketing_sources_get**](MarketingSourcesApi.md#get_active_marketing_sources_api_v1_marketing_sources_get) | **GET** /api/v1/marketing-sources | Get Active Marketing Sources


# **get_active_marketing_sources_api_v1_marketing_sources_get**
> object get_active_marketing_sources_api_v1_marketing_sources_get()

Get Active Marketing Sources

Return ``[{"code": ..., "label": ...}, ...]`` for active rows.

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
    api_instance = clienthub.MarketingSourcesApi(api_client)

    try:
        # Get Active Marketing Sources
        api_response = api_instance.get_active_marketing_sources_api_v1_marketing_sources_get()
        print("The response of MarketingSourcesApi->get_active_marketing_sources_api_v1_marketing_sources_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MarketingSourcesApi->get_active_marketing_sources_api_v1_marketing_sources_get: %s\n" % e)
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

