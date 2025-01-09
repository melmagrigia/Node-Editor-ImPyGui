import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.ass_variable import AssVariable  # noqa: E501
from openapi_server.models.operation import Operation  # noqa: E501
from openapi_server.models.variable import Variable  # noqa: E501
from openapi_server import util


def operation_operation_id_post(operation_id, request_body=None):  # noqa: E501
    """Execute an operation of the asset

     # noqa: E501

    :param operation_id: Operation id
    :type operation_id: str
    :param request_body: Parameters of the operation
    :type request_body: Dict[str, str]

    :rtype: Union[List[AssVariable], Tuple[List[AssVariable], int], Tuple[List[AssVariable], int, Dict[str, str]]
    """
    return 'do some magic!'


def operations_get():  # noqa: E501
    """Get executable operations of the asset

     # noqa: E501


    :rtype: Union[List[Operation], Tuple[List[Operation], int], Tuple[List[Operation], int, Dict[str, str]]
    """
    return 'do some magic!'


def state_get():  # noqa: E501
    """Get current state of the asset

     # noqa: E501


    :rtype: Union[List[AssVariable], Tuple[List[AssVariable], int], Tuple[List[AssVariable], int, Dict[str, str]]
    """
    return 'do some magic!'


def variables_get():  # noqa: E501
    """Get the variables of the asset

     # noqa: E501


    :rtype: Union[List[Variable], Tuple[List[Variable], int], Tuple[List[Variable], int, Dict[str, str]]
    """
    return 'do some magic!'
