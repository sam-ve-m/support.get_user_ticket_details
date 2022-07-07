# Jormungandr
from ..domain.exceptions import InvalidJwtToken

# Third party
from heimdall_client import Heimdall
from asyncio import get_event_loop


class JwtService:
    event_loop = get_event_loop()

    @classmethod
    def decode_jwt_and_get_unique_id(cls, jwt: str) -> str:
        jwt_content, heimdall_status_response = cls.event_loop.run_until_complete(
            Heimdall.decode_payload(jwt=jwt))
        unique_id = jwt_content["decoded_jwt"]['user'].get('unique_id')
        return unique_id

    @classmethod
    def apply_authentication_rules(cls, jwt: str):
        is_valid_jwt = cls.event_loop.run_until_complete(
            Heimdall.validate_jwt(jwt=jwt)
        )
        if not is_valid_jwt:
            raise InvalidJwtToken()
