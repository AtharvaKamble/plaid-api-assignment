import json
import requests
from time import sleep
from celery import shared_task
from rest_framework.response import Response


@shared_task()
def fetch_accounts_task(url, body, headers):
    res = requests.post(url, body, headers=headers)
    # print(url, body, headers)
    return res.json()
