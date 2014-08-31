#encoding: utf8
import requests
import json

ERR_NETWORK = -1
ERR_PROTOCOL = -2


def send(url, data):
    """
    Must not forget to describe the important error codes especially those
    that are not handling by requests library
    """
    try:
        response = requests.post(url, json.dumps(data))
        status_code = response.status_code
    except requests.exceptions.RequestException:
        status_code = ERR_NETWORK
    except requests.packages.urllib3.exceptions.ProtocolError:
        status_code = ERR_PROTOCOL
    return status_code
