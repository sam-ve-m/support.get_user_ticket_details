# Jormungandr
from src.domain.enums import InternalCode
from src.domain.exceptions import InvalidJwtToken, InvalidUniqueId, TicketNotFound
from src.domain.validator import Filter
from src.domain.response.model import ResponseModel
from src.services.jwt import JwtService
from src.services.get_user_ticket_details import TicketDetailsService

# Standards
from http import HTTPStatus

# Third party
from etria_logger import Gladsheim
from flask import request, Response


def get_user_ticket_details() -> Response:
    message = "Jormungandr::get_user_ticket_details"
    url_path = request.full_path
    raw_account_changes_params = request.args
    jwt = request.headers.get('x-thebes-answer')
    try:
        filter_params = Filter(**raw_account_changes_params)
        JwtService.apply_authentication_rules(jwt=jwt)
        decoded_jwt = JwtService.decode_jwt(jwt=jwt)
        client_account_change_service = TicketDetailsService(
            params=filter_params,
            url_path=url_path,
            decoded_jwt=decoded_jwt,
        )
        ticket = client_account_change_service.get_ticket_details()
        response = ResponseModel(
            result={'Ticket': ticket},
            success=True,
            code=InternalCode.SUCCESS
        ).build_http_response(status=HTTPStatus.OK)
        return response

    except InvalidUniqueId as ex:
        Gladsheim.error(error=ex, message=f"{message}::'The JWT unique id is not the same user unique id'")
        response = ResponseModel(
            message=ex.msg,
            success=False,
            code=InternalCode.JWT_INVALID,
        ).build_http_response(status=HTTPStatus.UNAUTHORIZED)
        return response

    except InvalidJwtToken as ex:
        Gladsheim.error(error=ex, message=f"{message}::Invalid JWT token")
        response = ResponseModel(
            success=False,
            code=InternalCode.JWT_INVALID,
            message=ex.msg,
        ).build_http_response(status=HTTPStatus.UNAUTHORIZED)
        return response

    except TicketNotFound as ex:
        Gladsheim.error(error=ex, message=f"{message}::No ticket was found with the specified id")
        response = ResponseModel(
            message=ex.msg,
            success=False,
            code=InternalCode.DATA_NOT_FOUND,
        ).build_http_response(status=HTTPStatus.NOT_FOUND)
        return response

    except ValueError as ex:
        Gladsheim.error(ex=ex, message=f'{message}::There are invalid format or extra parameters')
        response = ResponseModel(
            success=False,
            code=InternalCode.INVALID_PARAMS,
            message="There are invalid format or extra/missing parameters",
        ).build_http_response(status=HTTPStatus.BAD_REQUEST)
        return response

    except Exception as ex:
        Gladsheim.error(error=ex, message=f"{message}::{str(ex)}")
        response = ResponseModel(
            success=False,
            code=InternalCode.INTERNAL_SERVER_ERROR,
            message="Unexpected error occurred",
        ).build_http_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return response
