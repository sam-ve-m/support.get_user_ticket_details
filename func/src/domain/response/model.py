# Jormungandr
from func.src.domain.enum import CodeResponse

# Standards
from json import dumps

# Third party
from flask import Response
from nidavellir import Sindri


class ResponseModel:
    @staticmethod
    def build_response(success: bool, code: CodeResponse,  message: str = None, result: any = None) -> str:
        response_model = dumps(
            {
                "result": result,
                "message": message,
                "success": success,
                "code": code.value,
            },
            default=Sindri.resolver,
        )
        return response_model

    @staticmethod
    def build_http_response(response_model: str, status: int, mimetype: str = "application/json") -> Response:
        response = Response(
            response_model,
            mimetype=mimetype,
            status=status.value,
        )
        return response
