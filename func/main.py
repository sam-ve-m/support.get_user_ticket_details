# Jormungandr
from src.domain.enums import InternalCode
from src.domain.exceptions import InvalidJwtToken, InvalidUniqueId, TicketNotFound, InvalidTicketRequester
from src.domain.validator import TicketDetails
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
    raw_ticket_details = request.args
    jwt = request.headers.get('x-thebes-answer')
    try:
        ticket_details_validated = TicketDetails(**raw_ticket_details).dict()
        JwtService.apply_authentication_rules(jwt=jwt)
        unique_id = JwtService.decode_jwt_and_get_unique_id(jwt=jwt)
        user_ticket_service = TicketDetailsService(
            ticket_details_validated=ticket_details_validated,
            unique_id=unique_id,
        )
        result = user_ticket_service.get_ticket_details()
        response = ResponseModel(
            result=result,
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
        Gladsheim.warning(error=ex, message=f"{message}::Invalid JWT token")
        response = ResponseModel(
            success=False,
            code=InternalCode.JWT_INVALID,
            message=ex.msg,
        ).build_http_response(status=HTTPStatus.UNAUTHORIZED)
        return response

    except TicketNotFound as ex:
        Gladsheim.info(error=ex, message=f"{message}::No ticket was found with the specified id")
        response = ResponseModel(
            result={"ticket": None},
            message=ex.msg,
            success=False,
            code=InternalCode.DATA_NOT_FOUND,
        ).build_http_response(status=HTTPStatus.OK)
        return response

    except InvalidTicketRequester as ex:
        Gladsheim.info(error=ex, message=f"{message}::Invalid ticket owner")
        response = ResponseModel(
            result={"ticket": None},
            message=ex.msg,
            success=False,
            code=InternalCode.INVALID_OWNER,
        ).build_http_response(status=HTTPStatus.UNAUTHORIZED)
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
