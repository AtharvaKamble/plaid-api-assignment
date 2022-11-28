# Documentation

Refer to the bottom of this documentation on steps to start environment and server

### Signing up through the Plaid Link

Sign up for a Plaid Link account using your `client_id` and `secret`. This leads to obtaining a `link_token` that is used to initialize a Link.
Endpoint: `/signup`
Sample Input:

```
{
     "client_id": "6380f2599013a8001315bdf9",
     "secret": "f7673c6062441daac5570d459edb77",
     "user": {
       "client_user_id": "6380f2599013a8001315bdf9"
     },
     "client_name": "Plaid Test v0.0.2",
     "country_codes": [
       "US"
     ],
     "language": "en",
     "products": ["auth","transactions","assets"]
   }
```

### Signing in to the Plaid Link

Sign in for a Plaid Link account using your `client_id`, `secret` and `link_token`. 
Returns: All information about a given Link
Endpoint: `/signin`
Sample Input:

```
{
       "body": {
           "link_token": "link-sandbox-cabfce10-d486-40a5-8f20-efc3936b04bd"
       },
       "headers": {
           "content-type": "application/json",
           "PLAID-CLIENT-ID": "6380f2599013a8001315bdf9",
           "PLAID-SECRET": "f7673c6062441daac5570d459edb77"
       }
   }
```

### Initialize a Link

It creates a new Link, from the `link_token` given and this Link further provides a `public_token` (which expires after every 30 minutes). The `public_token` is essential in obtaining an `access_token`. It requires the financial institution ID and all the products you need to access. 
Endpoint: `/get-public-token`
Sample Input:

```
{
       "body": {
           "institution_id": "ins_109508",
           "initial_products": [
               "auth",
               "transactions"
           ]
       },
       "headers": {
           "content-type": "application/json",
           "PLAID-CLIENT-ID": "6380f2599013a8001315bdf9",
           "PLAID-SECRET": "f7673c6062441daac5570d459edb77"
       }
   }
```

### Exchange Token

The `public_token` has a short life-span and can/should be exchanged for an `access_token`. With this, further communication to the Plaid API is possible viz fetching accounts, transactions, etc.
Endpoint: `/exchange-token`
Sample Input:

```
   {
       "body": {
           "public_token": "public-sandbox-18ba2dad-aef2-4eb3-b655-6948703c9dce"
       },
       "headers": {
           "content-type": "application/json",
           "PLAID-CLIENT-ID": "6380f2599013a8001315bdf9",
           "PLAID-SECRET": "f7673c6062441daac5570d459edb77"
       }
   }
```

### Fetch transactions and accounts data

Fetches all transactions between a user and an Item (financial institution). This task is off-loaded to Celery as it is asynchronous in nature. We need to provide `start_date` and `end_date` as a range to fetch transactions.
Endpoint: `/transactions`
Sample Input:

```
{
       "body": {
           "access_token": "access-sandbox-40b0c7d5-674f-4904-a217-3be4251e1765",
           "start_date": "2021-11-27",
           "end_date": "2022-11-27"
       },
       "headers": {
           "content-type": "application/json",
           "PLAID-CLIENT-ID": "6380f2599013a8001315bdf9",
           "PLAID-SECRET": "f7673c6062441daac5570d459edb77"
       }
   }
```

### Fire webhooks voluntarily

Since in the `sandbox` mode, Plaid does not send or receive any webhooks, it allows developers to test webhooks by manually triggering a number of available webhooks. Ref [docs](https://plaid.com/docs/api/sandbox/#sandboxitemfire_webhook) for all available webhook actions.
Endpoint: `/fire-webhooks`
Sample Input:

```
   {
       "webhook_code": "SYNC_UPDATES_AVAILABLE"
   }
```

### View global webhook for notifications

This webhook URL is shared with Plaid and associated with our `access_token` and Item. Whenever a webhook is sent, this endpoint captures it.
Endpoint: `/webhook`

### Update webhook URL for a Link

If no URL has been associated with an `access_token` or in the scenario that one might need to change the URL, this endpoint is the one.
Endpoint: `/update-webhook-url`
Sample Input:

```
   {
       "body": {
          "access_token": "access-sandbox-d0fd8999-df53-4d89-8b9f-3a157c21bae0",
           "webhook": "http://localhost:8000/webhook"
       },
       "headers": {
           "content-type": "application/json",
           "PLAID-CLIENT-ID": "6380f2599013a8001315bdf9",
           "PLAID-SECRET": "f7673c6062441daac5570d459edb77"
       }
   }
```


Steps to start development server:

1. Install Python dependencies via `requirements.txt`
2. Application need three things to be running at once (`docker-compose` would be great in future additions)
   - Run the server: `python3 manage.py runserver`
   - Run Redis (message broker and task queue between Celery and Python): `redis-cli`
   - Run Celery: `celery -A assignment worker -l info`
3. You are ready to test the API on the django rest framework UI now!
