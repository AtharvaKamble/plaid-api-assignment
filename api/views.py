import os
import json
from shutil import ExecError
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .tasks import fetch_accounts_task
from .util import InvalidTokenError, handle_exception, validate_response


# The public_token is ephemereal and needs to be created a new one after 30 minutes
# The link_token and access_token however are permanent, though can be revoked voluntarily

#
# /link/token/create
# Creates a new link_token and return a public_token once a link has been initialized
# https://plaid.com/docs/api/tokens/#linktokencreate
#
@api_view(['POST'])
def sign_up(request):
    try:
        url = f"{os.environ.get('PLAID_DOMAIN_SANDBOX')}/link/token/create"
        body = request.data
        headers = {'content-type': 'application/json'}

        res = requests.post(url, data=json.dumps(body), headers=headers)
        validate_response(res.json())

        return Response({
            'response_from_Plaid': res.json(),
            'note_from_developer': f"With this link_token, you can obtain a public_token at the URL: {os.environ.get('SITE_DOMAIN_NAME')}/get-public-token."
        }, 200)
    except Exception as e:
        return handle_exception(e)


#
# /link/token/get
# Gets information about a previously created link_token from the sign_up and returns a public_token
# https://plaid.com/docs/api/tokens/#linktokenget
#
@api_view(['POST'])
def sign_in(request):
    try:
        url = f"{os.environ.get('PLAID_DOMAIN_SANDBOX')}/link/token/get"

        res = requests.post(url, json.dumps(request.data.get(
            'body')), headers=request.data.get('headers'))
        validate_response(res.json())

        return Response({
            'response_from_Plaid': res.json(),
            'note_from_developer': f"With this link_token, you can obtain a public_token at the URL: {os.environ.get('SITE_DOMAIN_NAME')}/get-public-token."
        }, status=200)
    except Exception as e:
        return handle_exception(e)


#
# /sandbox/item/public_token/create
# https://plaid.com/docs/api/sandbox/#sandboxpublic_tokencreate
# Create a link and then return a public_token which could be exchanged for an access_token
#
@api_view(['POST'])
def initialize_link(request):
    try:
        url = f"{os.environ.get('PLAID_DOMAIN_SANDBOX')}/sandbox/public_token/create"

        res = requests.post(url, json.dumps(
            request.data.get('body')), headers=request.data.get('headers'))

        validate_response(res.json())

        return Response({
            'response_from_Plaid': res.json(),
            'note_from_developer': f"You can exchange the public_token for an access_token at the URL: {os.environ.get('SITE_DOMAIN_NAME')}/exchange-token. The access-token is a crucial element, as it would let you connect to Items (financial institutions) and carry activities such as viewing transactions."
        }, status=200)
    except InvalidTokenError as e:
        return handle_exception(e)
    except Exception as e:
        return handle_exception(e)


#
# /item/public_token/exchange
# Exchange the public_token (link_token) for an access_token (secret)
# https://plaid.com/docs/api/tokens/#itempublic_tokenexchange
#
@ api_view(['POST'])
def exchange_token(request):
    try:
        url = f"{os.environ.get('PLAID_DOMAIN_SANDBOX')}/item/public_token/exchange"

        res = requests.post(url, json.dumps(request.data.get(
            'body')), headers=request.data.get('headers'))
        validate_response(res.json())

        return Response({
            'response_from_Plaid': res.json(),
            'note_from_developer': f"With this public_token, you can obtain an access_token at the URL: {os.environ.get('SITE_DOMAIN_NAME')}/exchange-token. The access-token is a crucial element, as it would let you connect to Items (financial institutions) and carry activities such as viewing transactions."
        }, status=200)
    except InvalidTokenError as e:
        return handle_exception(e)
    except Exception as e:
        return handle_exception(e)


#
# Fetch transactions and accounts data
#
@ api_view(['POST'])
def fetch_accounts(request):
    try:
        url = f"{os.environ.get('PLAID_DOMAIN_SANDBOX')}/transactions/get"

        res = fetch_accounts_task.delay(
            url, json.dumps(request.data.get('body')), request.data.get('headers'))

        validate_response(res.get())

        return Response(res.get(), status=200)
    except InvalidTokenError as e:
        return handle_exception(e)
    except Exception as e:
        return handle_exception(e)


#
# Fire a webhook voluntarily, as in sandbox mode for testing webhooks are generated automatically
#
@ api_view(['POST'])
def fire_webhook(request):
    #  {
    #       "webhook_code": "SYNC_UPDATES_AVAILABLE" | "NEW_ACCOUNTS_AVAILABLE" | "RECURRING_TRANSACTIONS_UPDATE"
    # }
    try:
        url = f"{os.environ.get('PLAID_DOMAIN_SANDBOX')}/sandbox/item/fire_webhook"
        body = {
            'access_token': 'access-sandbox-d0fd8999-df53-4d89-8b9f-3a157c21bae0',
            'webhook_code': request.data.get('webhook_code')
        }
        headers = {
            'content-type': 'application/json',
            'PLAID-CLIENT-ID': '6380f2599013a8001315bdf9',
            'PLAID-SECRET': 'f7673c6062441daac5570d459edb77',
        }

        res = requests.post(url, json.dumps(body), headers=headers)
        validate_response(res.json())

        return Response(res.json(), 200)
    except Exception as e:
        return handle_exception(e)


#
# Listen for webhook from Plaid. Plaid will ping this endpoint whenever it wants us to notify of any events.
# For eg. SYNC_UPDATES_AVAILABLE: New transactions is available
#         NEW_ACCOUNTS_AVAILABLE: If user creates more Items, this would be notified
#         PRODUCT_READY: Whenever an Asset Report is generated, this would be notified
#
@ api_view(['POST'])
def webhook(request):
    try:
        print(request.data)
        print('Webhook pinged!')
        return Response(200)
    except Exception as e:
        return handle_exception(e)


#
# Update the webhook URL associated with an access_token
#
@ api_view(['POST'])
def update_webhook_url(request):
    try:
        url = f"{os.environ.get('PLAID_DOMAIN_SANDBOX')}/item/webhook/update"
        body = {
            'access_token': 'access-sandbox-d0fd8999-df53-4d89-8b9f-3a157c21bae0',
            'webhook': f"{os.environ.get('SITE_DOMAIN_NAME')}/webhook"
        }
        headers = {
            'content-type': 'application/json',
            'PLAID-CLIENT-ID': '6380f2599013a8001315bdf9',
            'PLAID-SECRET': 'f7673c6062441daac5570d459edb77',
        }

        res = requests.post(url, json.dumps(request.data.get(
            'body')), headers=request.data.get('headers'))
        validate_response(res.json())

        return Response(res.json(), 200)
    except Exception as e:
        return handle_exception(e)
