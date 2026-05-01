# clienthub

Data-first customer intelligence microservice


## Installation & Usage

### Requirements

PHP 7.4 and later.
Should also work with PHP 8.0.

### Composer

To install the bindings via [Composer](https://getcomposer.org/), add the following to `composer.json`:

```json
{
  "repositories": [
    {
      "type": "vcs",
      "url": "https://github.com/GIT_USER_ID/GIT_REPO_ID.git"
    }
  ],
  "require": {
    "GIT_USER_ID/GIT_REPO_ID": "*@dev"
  }
}
```

Then run `composer install`

### Manual Installation

Download the files and include `autoload.php`:

```php
<?php
require_once('/path/to/clienthub/vendor/autoload.php');
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```php
<?php
require_once(__DIR__ . '/vendor/autoload.php');



// Configure API key authorization: APIKeyHeader
$config = ClientHub\Configuration::getDefaultConfiguration()->setApiKey('X-API-Key', 'YOUR_API_KEY');
// Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
// $config = ClientHub\Configuration::getDefaultConfiguration()->setApiKeyPrefix('X-API-Key', 'Bearer');


$apiInstance = new ClientHub\Api\AdminApi(
    // If you want use custom http client, pass your client which implements `GuzzleHttp\ClientInterface`.
    // This is optional, `GuzzleHttp\Client` will be used as default.
    new GuzzleHttp\Client(),
    $config
);
$uuid = 'uuid_example'; // string
$api_key_create = new \ClientHub\Model\ApiKeyCreate(); // \ClientHub\Model\ApiKeyCreate

try {
    $result = $apiInstance->createApiKeyApiV1AdminSourcesUuidApiKeysPost($uuid, $api_key_create);
    print_r($result);
} catch (Exception $e) {
    echo 'Exception when calling AdminApi->createApiKeyApiV1AdminSourcesUuidApiKeysPost: ', $e->getMessage(), PHP_EOL;
}

```

## API Endpoints

All URIs are relative to *http://localhost*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AdminApi* | [**createApiKeyApiV1AdminSourcesUuidApiKeysPost**](docs/Api/AdminApi.md#createapikeyapiv1adminsourcesuuidapikeyspost) | **POST** /api/v1/admin/sources/{uuid}/api-keys | Create Api Key
*AdminApi* | [**createSourceApiV1AdminSourcesPost**](docs/Api/AdminApi.md#createsourceapiv1adminsourcespost) | **POST** /api/v1/admin/sources | Create Source
*AdminApi* | [**deleteSourceApiV1AdminSourcesUuidDelete**](docs/Api/AdminApi.md#deletesourceapiv1adminsourcesuuiddelete) | **DELETE** /api/v1/admin/sources/{uuid} | Delete Source
*AdminApi* | [**getSourceApiV1AdminSourcesUuidGet**](docs/Api/AdminApi.md#getsourceapiv1adminsourcesuuidget) | **GET** /api/v1/admin/sources/{uuid} | Get Source
*AdminApi* | [**listApiKeysApiV1AdminSourcesUuidApiKeysGet**](docs/Api/AdminApi.md#listapikeysapiv1adminsourcesuuidapikeysget) | **GET** /api/v1/admin/sources/{uuid}/api-keys | List Api Keys
*AdminApi* | [**listEventsApiV1AdminEventsGet**](docs/Api/AdminApi.md#listeventsapiv1admineventsget) | **GET** /api/v1/admin/events | List Events
*AdminApi* | [**listSourcesApiV1AdminSourcesGet**](docs/Api/AdminApi.md#listsourcesapiv1adminsourcesget) | **GET** /api/v1/admin/sources | List Sources
*AdminApi* | [**revokeApiKeyApiV1AdminApiKeysUuidDelete**](docs/Api/AdminApi.md#revokeapikeyapiv1adminapikeysuuiddelete) | **DELETE** /api/v1/admin/api-keys/{uuid} | Revoke Api Key
*AdminApi* | [**updateSourceApiV1AdminSourcesUuidPut**](docs/Api/AdminApi.md#updatesourceapiv1adminsourcesuuidput) | **PUT** /api/v1/admin/sources/{uuid} | Update Source
*AffiliationsApi* | [**createAffiliationEndpointApiV1ContactsContactUuidAffiliationsPost**](docs/Api/AffiliationsApi.md#createaffiliationendpointapiv1contactscontactuuidaffiliationspost) | **POST** /api/v1/contacts/{contact_uuid}/affiliations | Create Affiliation Endpoint
*AffiliationsApi* | [**deleteAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidDelete**](docs/Api/AffiliationsApi.md#deleteaffiliationendpointapiv1contactscontactuuidaffiliationsaffiliationuuiddelete) | **DELETE** /api/v1/contacts/{contact_uuid}/affiliations/{affiliation_uuid} | Delete Affiliation Endpoint
*AffiliationsApi* | [**listAffiliationsEndpointApiV1ContactsContactUuidAffiliationsGet**](docs/Api/AffiliationsApi.md#listaffiliationsendpointapiv1contactscontactuuidaffiliationsget) | **GET** /api/v1/contacts/{contact_uuid}/affiliations | List Affiliations Endpoint
*AffiliationsApi* | [**updateAffiliationEndpointApiV1ContactsContactUuidAffiliationsAffiliationUuidPut**](docs/Api/AffiliationsApi.md#updateaffiliationendpointapiv1contactscontactuuidaffiliationsaffiliationuuidput) | **PUT** /api/v1/contacts/{contact_uuid}/affiliations/{affiliation_uuid} | Update Affiliation Endpoint
*CommunicationsApi* | [**createCommunicationApiV1CommunicationsPost**](docs/Api/CommunicationsApi.md#createcommunicationapiv1communicationspost) | **POST** /api/v1/communications | Create Communication
*CommunicationsApi* | [**getCommunicationApiV1CommunicationsUuidGet**](docs/Api/CommunicationsApi.md#getcommunicationapiv1communicationsuuidget) | **GET** /api/v1/communications/{uuid} | Get Communication
*CommunicationsApi* | [**listCommunicationsApiV1CommunicationsGet**](docs/Api/CommunicationsApi.md#listcommunicationsapiv1communicationsget) | **GET** /api/v1/communications | List Communications
*ContactsApi* | [**contactSummaryEndpointApiV1ContactsUuidSummaryGet**](docs/Api/ContactsApi.md#contactsummaryendpointapiv1contactsuuidsummaryget) | **GET** /api/v1/contacts/{uuid}/summary | Contact Summary Endpoint
*ContactsApi* | [**convertContactEndpointApiV1ContactsUuidConvertPost**](docs/Api/ContactsApi.md#convertcontactendpointapiv1contactsuuidconvertpost) | **POST** /api/v1/contacts/{uuid}/convert | Convert Contact Endpoint
*ContactsApi* | [**createContactEndpointApiV1ContactsPost**](docs/Api/ContactsApi.md#createcontactendpointapiv1contactspost) | **POST** /api/v1/contacts | Create Contact Endpoint
*ContactsApi* | [**deleteContactEndpointApiV1ContactsUuidDelete**](docs/Api/ContactsApi.md#deletecontactendpointapiv1contactsuuiddelete) | **DELETE** /api/v1/contacts/{uuid} | Delete Contact Endpoint
*ContactsApi* | [**deletePreferenceApiV1ContactsUuidPreferencesKeyDelete**](docs/Api/ContactsApi.md#deletepreferenceapiv1contactsuuidpreferenceskeydelete) | **DELETE** /api/v1/contacts/{uuid}/preferences/{key} | Delete Preference
*ContactsApi* | [**getContactEndpointApiV1ContactsUuidGet**](docs/Api/ContactsApi.md#getcontactendpointapiv1contactsuuidget) | **GET** /api/v1/contacts/{uuid} | Get Contact Endpoint
*ContactsApi* | [**getMarketingOptoutsApiV1ContactsUuidMarketingGet**](docs/Api/ContactsApi.md#getmarketingoptoutsapiv1contactsuuidmarketingget) | **GET** /api/v1/contacts/{uuid}/marketing | Get Marketing Optouts
*ContactsApi* | [**listContactsEndpointApiV1ContactsGet**](docs/Api/ContactsApi.md#listcontactsendpointapiv1contactsget) | **GET** /api/v1/contacts | List Contacts Endpoint
*ContactsApi* | [**listPreferencesApiV1ContactsUuidPreferencesGet**](docs/Api/ContactsApi.md#listpreferencesapiv1contactsuuidpreferencesget) | **GET** /api/v1/contacts/{uuid}/preferences | List Preferences
*ContactsApi* | [**setPreferenceApiV1ContactsUuidPreferencesKeyPut**](docs/Api/ContactsApi.md#setpreferenceapiv1contactsuuidpreferenceskeyput) | **PUT** /api/v1/contacts/{uuid}/preferences/{key} | Set Preference
*ContactsApi* | [**updateContactEndpointApiV1ContactsUuidPut**](docs/Api/ContactsApi.md#updatecontactendpointapiv1contactsuuidput) | **PUT** /api/v1/contacts/{uuid} | Update Contact Endpoint
*ContactsApi* | [**updateMarketingOptoutsApiV1ContactsUuidMarketingPut**](docs/Api/ContactsApi.md#updatemarketingoptoutsapiv1contactsuuidmarketingput) | **PUT** /api/v1/contacts/{uuid}/marketing | Update Marketing Optouts
*HealthApi* | [**healthCheckApiV1HealthGet**](docs/Api/HealthApi.md#healthcheckapiv1healthget) | **GET** /api/v1/health | Health Check
*InvoicesApi* | [**createInvoiceApiV1InvoicesPost**](docs/Api/InvoicesApi.md#createinvoiceapiv1invoicespost) | **POST** /api/v1/invoices | Create Invoice
*InvoicesApi* | [**getInvoiceApiV1InvoicesUuidGet**](docs/Api/InvoicesApi.md#getinvoiceapiv1invoicesuuidget) | **GET** /api/v1/invoices/{uuid} | Get Invoice
*InvoicesApi* | [**listInvoicesApiV1InvoicesGet**](docs/Api/InvoicesApi.md#listinvoicesapiv1invoicesget) | **GET** /api/v1/invoices | List Invoices
*InvoicesApi* | [**recordPaymentApiV1InvoicesUuidPaymentsPost**](docs/Api/InvoicesApi.md#recordpaymentapiv1invoicesuuidpaymentspost) | **POST** /api/v1/invoices/{uuid}/payments | Record Payment
*LookupApi* | [**lookupEmailApiV1LookupEmailEmailGet**](docs/Api/LookupApi.md#lookupemailapiv1lookupemailemailget) | **GET** /api/v1/lookup/email/{email} | Lookup Email
*LookupApi* | [**lookupPhoneApiV1LookupPhoneNumberGet**](docs/Api/LookupApi.md#lookupphoneapiv1lookupphonenumberget) | **GET** /api/v1/lookup/phone/{number} | Lookup Phone
*MarketingSourcesApi* | [**getActiveMarketingSourcesApiV1MarketingSourcesGet**](docs/Api/MarketingSourcesApi.md#getactivemarketingsourcesapiv1marketingsourcesget) | **GET** /api/v1/marketing-sources | Get Active Marketing Sources
*OrdersApi* | [**changeOrderStatusApiV1OrdersUuidStatusPost**](docs/Api/OrdersApi.md#changeorderstatusapiv1ordersuuidstatuspost) | **POST** /api/v1/orders/{uuid}/status | Change Order Status
*OrdersApi* | [**createOrderApiV1OrdersPost**](docs/Api/OrdersApi.md#createorderapiv1orderspost) | **POST** /api/v1/orders | Create Order
*OrdersApi* | [**deleteOrderApiV1OrdersUuidDelete**](docs/Api/OrdersApi.md#deleteorderapiv1ordersuuiddelete) | **DELETE** /api/v1/orders/{uuid} | Delete Order
*OrdersApi* | [**getOrderApiV1OrdersUuidGet**](docs/Api/OrdersApi.md#getorderapiv1ordersuuidget) | **GET** /api/v1/orders/{uuid} | Get Order
*OrdersApi* | [**listOrdersApiV1OrdersGet**](docs/Api/OrdersApi.md#listordersapiv1ordersget) | **GET** /api/v1/orders | List Orders
*OrganizationsApi* | [**createOrganizationApiV1OrganizationsPost**](docs/Api/OrganizationsApi.md#createorganizationapiv1organizationspost) | **POST** /api/v1/organizations | Create Organization
*OrganizationsApi* | [**deleteOrganizationApiV1OrganizationsUuidDelete**](docs/Api/OrganizationsApi.md#deleteorganizationapiv1organizationsuuiddelete) | **DELETE** /api/v1/organizations/{uuid} | Delete Organization
*OrganizationsApi* | [**getOrganizationApiV1OrganizationsUuidGet**](docs/Api/OrganizationsApi.md#getorganizationapiv1organizationsuuidget) | **GET** /api/v1/organizations/{uuid} | Get Organization
*OrganizationsApi* | [**listOrganizationsApiV1OrganizationsGet**](docs/Api/OrganizationsApi.md#listorganizationsapiv1organizationsget) | **GET** /api/v1/organizations | List Organizations
*OrganizationsApi* | [**updateOrganizationApiV1OrganizationsUuidPut**](docs/Api/OrganizationsApi.md#updateorganizationapiv1organizationsuuidput) | **PUT** /api/v1/organizations/{uuid} | Update Organization
*SettingsApi* | [**getSettingsApiV1SettingsGet**](docs/Api/SettingsApi.md#getsettingsapiv1settingsget) | **GET** /api/v1/settings | Get Settings
*SettingsApi* | [**updateSettingsApiV1SettingsPut**](docs/Api/SettingsApi.md#updatesettingsapiv1settingsput) | **PUT** /api/v1/settings | Update Settings
*SpamAdminApi* | [**adminCreatePatternApiV1AdminSpamPatternsPost**](docs/Api/SpamAdminApi.md#admincreatepatternapiv1adminspampatternspost) | **POST** /api/v1/admin/spam-patterns | Admin Create Pattern
*SpamAdminApi* | [**adminDeletePatternApiV1AdminSpamPatternsUuidDelete**](docs/Api/SpamAdminApi.md#admindeletepatternapiv1adminspampatternsuuiddelete) | **DELETE** /api/v1/admin/spam-patterns/{uuid} | Admin Delete Pattern
*SpamAdminApi* | [**adminEventStatsApiV1AdminSpamEventsStatsGet**](docs/Api/SpamAdminApi.md#admineventstatsapiv1adminspameventsstatsget) | **GET** /api/v1/admin/spam-events/stats | Admin Event Stats
*SpamAdminApi* | [**adminListEventsApiV1AdminSpamEventsGet**](docs/Api/SpamAdminApi.md#adminlisteventsapiv1adminspameventsget) | **GET** /api/v1/admin/spam-events | Admin List Events
*SpamAdminApi* | [**adminListPatternsApiV1AdminSpamPatternsGet**](docs/Api/SpamAdminApi.md#adminlistpatternsapiv1adminspampatternsget) | **GET** /api/v1/admin/spam-patterns | Admin List Patterns
*SpamAdminApi* | [**adminMarkEventFalsePositiveApiV1AdminSpamEventsUuidMarkFalsePositivePost**](docs/Api/SpamAdminApi.md#adminmarkeventfalsepositiveapiv1adminspameventsuuidmarkfalsepositivepost) | **POST** /api/v1/admin/spam-events/{uuid}/mark-false-positive | Admin Mark Event False Positive
*SpamAdminApi* | [**adminUpdatePatternApiV1AdminSpamPatternsUuidPut**](docs/Api/SpamAdminApi.md#adminupdatepatternapiv1adminspampatternsuuidput) | **PUT** /api/v1/admin/spam-patterns/{uuid} | Admin Update Pattern
*SpamPatternsApi* | [**getActivePatternsPublicApiV1SpamPatternsGet**](docs/Api/SpamPatternsApi.md#getactivepatternspublicapiv1spampatternsget) | **GET** /api/v1/spam-patterns | Get Active Patterns Public
*WebhooksApi* | [**chatwootWebhookApiV1WebhooksChatwootPost**](docs/Api/WebhooksApi.md#chatwootwebhookapiv1webhookschatwootpost) | **POST** /api/v1/webhooks/chatwoot | Chatwoot Webhook
*WebhooksApi* | [**invoiceninjaWebhookApiV1WebhooksInvoiceninjaPost**](docs/Api/WebhooksApi.md#invoiceninjawebhookapiv1webhooksinvoiceninjapost) | **POST** /api/v1/webhooks/invoiceninja | Invoiceninja Webhook

## Models

- [AffiliationCreate](docs/Model/AffiliationCreate.md)
- [AffiliationUpdate](docs/Model/AffiliationUpdate.md)
- [Amount](docs/Model/Amount.md)
- [ApiKeyCreate](docs/Model/ApiKeyCreate.md)
- [CommCreate](docs/Model/CommCreate.md)
- [ContactCreate](docs/Model/ContactCreate.md)
- [ContactCreateEmail](docs/Model/ContactCreateEmail.md)
- [ContactCreatePhone](docs/Model/ContactCreatePhone.md)
- [ContactUpdate](docs/Model/ContactUpdate.md)
- [DiscountAmount](docs/Model/DiscountAmount.md)
- [HTTPValidationError](docs/Model/HTTPValidationError.md)
- [InlineAffiliationCreate](docs/Model/InlineAffiliationCreate.md)
- [InvoiceCreate](docs/Model/InvoiceCreate.md)
- [MarketingOptOuts](docs/Model/MarketingOptOuts.md)
- [OrderCreate](docs/Model/OrderCreate.md)
- [OrderItemCreate](docs/Model/OrderItemCreate.md)
- [OrgCreate](docs/Model/OrgCreate.md)
- [OrgUpdate](docs/Model/OrgUpdate.md)
- [PaymentCreate](docs/Model/PaymentCreate.md)
- [PreferenceSet](docs/Model/PreferenceSet.md)
- [Quantity](docs/Model/Quantity.md)
- [SettingsUpdate](docs/Model/SettingsUpdate.md)
- [SourceCreate](docs/Model/SourceCreate.md)
- [SourceUpdate](docs/Model/SourceUpdate.md)
- [SpamPatternCreate](docs/Model/SpamPatternCreate.md)
- [SpamPatternUpdate](docs/Model/SpamPatternUpdate.md)
- [StatusChange](docs/Model/StatusChange.md)
- [Subtotal](docs/Model/Subtotal.md)
- [TaxAmount](docs/Model/TaxAmount.md)
- [UnitPrice](docs/Model/UnitPrice.md)
- [ValidationError](docs/Model/ValidationError.md)
- [ValidationErrorLocInner](docs/Model/ValidationErrorLocInner.md)

## Authorization

Authentication schemes defined for the API:
### APIKeyHeader

- **Type**: API key
- **API key parameter name**: X-API-Key
- **Location**: HTTP header


## Tests

To run the tests, use:

```bash
composer install
vendor/bin/phpunit
```

## Author



## About this package

This PHP package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: `0.3.3`
    - Generator version: `7.12.0`
- Build package: `org.openapitools.codegen.languages.PhpClientCodegen`
