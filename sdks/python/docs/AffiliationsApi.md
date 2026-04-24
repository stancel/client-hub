# clienthub.AffiliationsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_post**](AffiliationsApi.md#create_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_post) | **POST** /api/v1/contacts/{contact_uuid}/affiliations | Create Affiliation Endpoint
[**delete_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_affiliation_uuid_delete**](AffiliationsApi.md#delete_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_affiliation_uuid_delete) | **DELETE** /api/v1/contacts/{contact_uuid}/affiliations/{affiliation_uuid} | Delete Affiliation Endpoint
[**list_affiliations_endpoint_api_v1_contacts_contact_uuid_affiliations_get**](AffiliationsApi.md#list_affiliations_endpoint_api_v1_contacts_contact_uuid_affiliations_get) | **GET** /api/v1/contacts/{contact_uuid}/affiliations | List Affiliations Endpoint
[**update_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_affiliation_uuid_put**](AffiliationsApi.md#update_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_affiliation_uuid_put) | **PUT** /api/v1/contacts/{contact_uuid}/affiliations/{affiliation_uuid} | Update Affiliation Endpoint


# **create_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_post**
> object create_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_post(contact_uuid, affiliation_create)

Create Affiliation Endpoint

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.affiliation_create import AffiliationCreate
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
    api_instance = clienthub.AffiliationsApi(api_client)
    contact_uuid = 'contact_uuid_example' # str | 
    affiliation_create = clienthub.AffiliationCreate() # AffiliationCreate | 

    try:
        # Create Affiliation Endpoint
        api_response = api_instance.create_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_post(contact_uuid, affiliation_create)
        print("The response of AffiliationsApi->create_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AffiliationsApi->create_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **contact_uuid** | **str**|  | 
 **affiliation_create** | [**AffiliationCreate**](AffiliationCreate.md)|  | 

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

# **delete_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_affiliation_uuid_delete**
> delete_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_affiliation_uuid_delete(contact_uuid, affiliation_uuid)

Delete Affiliation Endpoint

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
    api_instance = clienthub.AffiliationsApi(api_client)
    contact_uuid = 'contact_uuid_example' # str | 
    affiliation_uuid = 'affiliation_uuid_example' # str | 

    try:
        # Delete Affiliation Endpoint
        api_instance.delete_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_affiliation_uuid_delete(contact_uuid, affiliation_uuid)
    except Exception as e:
        print("Exception when calling AffiliationsApi->delete_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_affiliation_uuid_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **contact_uuid** | **str**|  | 
 **affiliation_uuid** | **str**|  | 

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

# **list_affiliations_endpoint_api_v1_contacts_contact_uuid_affiliations_get**
> object list_affiliations_endpoint_api_v1_contacts_contact_uuid_affiliations_get(contact_uuid, active_only=active_only)

List Affiliations Endpoint

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
    api_instance = clienthub.AffiliationsApi(api_client)
    contact_uuid = 'contact_uuid_example' # str | 
    active_only = True # bool |  (optional) (default to True)

    try:
        # List Affiliations Endpoint
        api_response = api_instance.list_affiliations_endpoint_api_v1_contacts_contact_uuid_affiliations_get(contact_uuid, active_only=active_only)
        print("The response of AffiliationsApi->list_affiliations_endpoint_api_v1_contacts_contact_uuid_affiliations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AffiliationsApi->list_affiliations_endpoint_api_v1_contacts_contact_uuid_affiliations_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **contact_uuid** | **str**|  | 
 **active_only** | **bool**|  | [optional] [default to True]

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

# **update_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_affiliation_uuid_put**
> object update_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_affiliation_uuid_put(contact_uuid, affiliation_uuid, affiliation_update)

Update Affiliation Endpoint

### Example

* Api Key Authentication (APIKeyHeader):

```python
import clienthub
from clienthub.models.affiliation_update import AffiliationUpdate
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
    api_instance = clienthub.AffiliationsApi(api_client)
    contact_uuid = 'contact_uuid_example' # str | 
    affiliation_uuid = 'affiliation_uuid_example' # str | 
    affiliation_update = clienthub.AffiliationUpdate() # AffiliationUpdate | 

    try:
        # Update Affiliation Endpoint
        api_response = api_instance.update_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_affiliation_uuid_put(contact_uuid, affiliation_uuid, affiliation_update)
        print("The response of AffiliationsApi->update_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_affiliation_uuid_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AffiliationsApi->update_affiliation_endpoint_api_v1_contacts_contact_uuid_affiliations_affiliation_uuid_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **contact_uuid** | **str**|  | 
 **affiliation_uuid** | **str**|  | 
 **affiliation_update** | [**AffiliationUpdate**](AffiliationUpdate.md)|  | 

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

