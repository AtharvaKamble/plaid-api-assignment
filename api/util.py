from rest_framework.response import Response
from rest_framework.exceptions import ParseError


#
# Catch exceptions raise by validate_response(res) and return error message
#
def handle_exception(e):
    res = dict()
    res['error_message'] = str(e)

    return Response(res, status=500)


#
# See if error_message is returned by the Plaid API
# If yes, then raise proper exceptions, which would then be caught by handle_exception(e)
#
def validate_response(res):
    err_code = res.get('error_code')
    message = res.get('error_message')

    if err_code == 'INVALID_PUBLIC_TOKEN':
        raise InvalidTokenError(message)
    elif err_code == 'INVALID_ACCESS_TOKEN':
        raise InvalidTokenError(message)
    elif err_code == 'SANDBOX_WEBHOOK_INVALID':
        raise InvalidWebhookError(message)
    elif err_code == 'MISSING_FIELDS':
        raise InvalidInputError(message)


class InvalidTokenError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidWebhookError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidInputError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
