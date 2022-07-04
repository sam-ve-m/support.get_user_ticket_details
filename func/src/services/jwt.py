# Jormungandr
from ..domain.exceptions import InvalidJwtToken

# Third party
from heimdall_client import Heimdall
from asyncio import get_event_loop


class JwtService:
    event_loop = get_event_loop()

    @classmethod
    def decode_jwt(cls, jwt: str) -> dict:
        jwt_content, heimdall_status_response = cls.event_loop.run_until_complete(
            Heimdall.decode_payload(jwt=jwt))
        decoded_jwt = jwt_content["decoded_jwt"]
        return decoded_jwt

    @classmethod
    def apply_authentication_rules(cls, jwt: str):
        is_valid_jwt = cls.event_loop.run_until_complete(
            Heimdall.validate_jwt(jwt=jwt)
        )
        if not is_valid_jwt:
            raise InvalidJwtToken()
