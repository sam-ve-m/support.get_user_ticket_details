from flask import request, Response
import asyncio
import json

from etria_logger import Gladsheim
from heimdall_client.bifrost import Heimdall
from nidavellir import Sindri
from src.validator import Filter
from src.service import TicketDetailsService

event_loop = asyncio.get_event_loop()


def get_user_ticket_details():
    url_path = request.full_path
    raw_account_changes_params = request.args
    x_thebes_answer = request.headers.get('x-thebes-answer')
    heimdall_client = Heimdall()
    try:
        http_status = 403
        payload = {'status': False}
        is_a_valid_jwt = event_loop.run_until_complete(heimdall_client.validate_jwt(jwt=x_thebes_answer))
        if is_a_valid_jwt:
            jwt_content, heimdall_status = event_loop.run_until_complete(
                heimdall_client.decode_payload(jwt=x_thebes_answer)
            )
            filter_params = Filter(**raw_account_changes_params)
            client_account_change_service = TicketDetailsService(
                params=filter_params,
                url_path=url_path,
                x_thebes_answer=jwt_content['decoded_jwt'],
            )
            ticket = client_account_change_service.get_tickets()
            payload.update({'status': True, 'ticket': ticket})
            http_status = 200
            response = Response(
                json.dumps(payload, default=Sindri.resolver),
                mimetype='application/json',
                status=http_status,
            )
        return response
    except Exception as e:
        message = 'Fission: get_user_ticket_details'
        Gladsheim.error(e, message)
        response = Response(
            json.dumps({'error': {'message': str(e)}, 'status': False}),
            mimetype='application/json',
            status=400,
        )
        return response
