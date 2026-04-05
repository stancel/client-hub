# clienthub.WebhooksApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**chatwoot_webhook_api_v1_webhooks_chatwoot_post**](WebhooksApi.md#chatwoot_webhook_api_v1_webhooks_chatwoot_post) | **POST** /api/v1/webhooks/chatwoot | Chatwoot Webhook
[**invoiceninja_webhook_api_v1_webhooks_invoiceninja_post**](WebhooksApi.md#invoiceninja_webhook_api_v1_webhooks_invoiceninja_post) | **POST** /api/v1/webhooks/invoiceninja | Invoiceninja Webhook


# **chatwoot_webhook_api_v1_webhooks_chatwoot_post**
> object chatwoot_webhook_api_v1_webhooks_chatwoot_post()

Chatwoot Webhook

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
    api_instance = clienthub.WebhooksApi(api_client)

    try:
        # Chatwoot Webhook
        api_response = api_instance.chatwoot_webhook_api_v1_webhooks_chatwoot_post()
        print("The response of WebhooksApi->chatwoot_webhook_api_v1_webhooks_chatwoot_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->chatwoot_webhook_api_v1_webhooks_chatwoot_post: %s\n" % e)
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

# **invoiceninja_webhook_api_v1_webhooks_invoiceninja_post**
> object invoiceninja_webhook_api_v1_webhooks_invoiceninja_post()

Invoiceninja Webhook

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
    api_instance = clienthub.WebhooksApi(api_client)

    try:
        # Invoiceninja Webhook
        api_response = api_instance.invoiceninja_webhook_api_v1_webhooks_invoiceninja_post()
        print("The response of WebhooksApi->invoiceninja_webhook_api_v1_webhooks_invoiceninja_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->invoiceninja_webhook_api_v1_webhooks_invoiceninja_post: %s\n" % e)
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

