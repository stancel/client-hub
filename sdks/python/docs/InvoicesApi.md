# clienthub.InvoicesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_invoice_api_v1_invoices_post**](InvoicesApi.md#create_invoice_api_v1_invoices_post) | **POST** /api/v1/invoices | Create Invoice
[**get_invoice_api_v1_invoices_uuid_get**](InvoicesApi.md#get_invoice_api_v1_invoices_uuid_get) | **GET** /api/v1/invoices/{uuid} | Get Invoice
[**list_invoices_api_v1_invoices_get**](InvoicesApi.md#list_invoices_api_v1_invoices_get) | **GET** /api/v1/invoices | List Invoices
[**record_payment_api_v1_invoices_uuid_payments_post**](InvoicesApi.md#record_payment_api_v1_invoices_uuid_payments_post) | **POST** /api/v1/invoices/{uuid}/payments | Record Payment


# **create_invoice_api_v1_invoices_post**
> object create_invoice_api_v1_invoices_post(invoice_create)

Create Invoice

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.invoice_create import InvoiceCreate
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
    api_instance = clienthub.InvoicesApi(api_client)
    invoice_create = clienthub.InvoiceCreate() # InvoiceCreate | 

    try:
        # Create Invoice
        api_response = api_instance.create_invoice_api_v1_invoices_post(invoice_create)
        print("The response of InvoicesApi->create_invoice_api_v1_invoices_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->create_invoice_api_v1_invoices_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invoice_create** | [**InvoiceCreate**](InvoiceCreate.md)|  | 

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

# **get_invoice_api_v1_invoices_uuid_get**
> object get_invoice_api_v1_invoices_uuid_get(uuid)

Get Invoice

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
    api_instance = clienthub.InvoicesApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Invoice
        api_response = api_instance.get_invoice_api_v1_invoices_uuid_get(uuid)
        print("The response of InvoicesApi->get_invoice_api_v1_invoices_uuid_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->get_invoice_api_v1_invoices_uuid_get: %s\n" % e)
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

# **list_invoices_api_v1_invoices_get**
> object list_invoices_api_v1_invoices_get(page=page, per_page=per_page, status=status)

List Invoices

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
    api_instance = clienthub.InvoicesApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    per_page = 25 # int |  (optional) (default to 25)
    status = 'status_example' # str |  (optional)

    try:
        # List Invoices
        api_response = api_instance.list_invoices_api_v1_invoices_get(page=page, per_page=per_page, status=status)
        print("The response of InvoicesApi->list_invoices_api_v1_invoices_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->list_invoices_api_v1_invoices_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**|  | [optional] [default to 1]
 **per_page** | **int**|  | [optional] [default to 25]
 **status** | **str**|  | [optional] 

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

# **record_payment_api_v1_invoices_uuid_payments_post**
> object record_payment_api_v1_invoices_uuid_payments_post(uuid, payment_create)

Record Payment

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.payment_create import PaymentCreate
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
    api_instance = clienthub.InvoicesApi(api_client)
    uuid = 'uuid_example' # str | 
    payment_create = clienthub.PaymentCreate() # PaymentCreate | 

    try:
        # Record Payment
        api_response = api_instance.record_payment_api_v1_invoices_uuid_payments_post(uuid, payment_create)
        print("The response of InvoicesApi->record_payment_api_v1_invoices_uuid_payments_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InvoicesApi->record_payment_api_v1_invoices_uuid_payments_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **payment_create** | [**PaymentCreate**](PaymentCreate.md)|  | 

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

