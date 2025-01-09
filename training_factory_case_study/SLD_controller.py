import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.ass_variable import AssVariable  # noqa: E501
from openapi_server.models.operation import Operation  # noqa: E501
from openapi_server.models.variable import Variable  # noqa: E501
from openapi_server import util

from training_factory_utils import *

def operation_operation_id_post(operation_id, request_body=None):  # noqa: E501
    """Execute an operation of the asset

     # noqa: E501

    :param operation_id: Operation id
    :type operation_id: str
    :param request_body: Parameters of the operation
    :type request_body: Dict[str, str]

    :rtype: Union[List[AssVariable], Tuple[List[AssVariable], int], Tuple[List[AssVariable], int, Dict[str, str]]
    """
    # Define the payload and URL
    payload = {operation_id: True}
    url = "http://192.168.0.5:1880/SLD/operation"

    # Perform the POST request
    response = perform_post_request(payload, url)

    # Check the response
    if response:
        if response.status_code == 200:
            print("POST request successful.")
            print("Response JSON:", response.json())
        else:
            print(f"POST request failed with status code: {response.status_code}")
            print("Response Text:", response.text)
    else:
        print("Failed to perform the POST request.")
    return response


def operations_get():  # noqa: E501
    """Get executable operations of the asset

     # noqa: E501


    :rtype: Union[List[Operation], Tuple[List[Operation], int], Tuple[List[Operation], int, Dict[str, str]]
    """
    operations = get_operation_ids("SLD.json")
    return operations

def state_get():  # noqa: E501
    """Get current state of the asset

     # noqa: E501


    :rtype: Union[List[AssVariable], Tuple[List[AssVariable], int], Tuple[List[AssVariable], int, Dict[str, str]]
    """
    # Define the URL
    url = "http://192.168.0.5:1880/SLD/state"

    # Perform the GET request
    response = perform_get_request(url)

    # Check the response
    if response:
        if response.status_code == 200:
            print("GET request successful.")
            print("Response JSON:", response.json())
        else:
            print(f"GET request failed with status code: {response.status_code}")
            print("Response Text:", response.text)
    else:
        print("Failed to perform the GET request.")
    return response


def variables_get():  # noqa: E501
    """Get the variables of the asset

     # noqa: E501


    :rtype: Union[List[Variable], Tuple[List[Variable], int], Tuple[List[Variable], int, Dict[str, str]]
    """
    variables = get_distinct_non_logical_substrings("SLD.json")

    return variables
