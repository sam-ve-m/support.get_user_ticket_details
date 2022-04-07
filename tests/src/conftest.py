from func.src.service import TicketDetailsService
from func.src.validator import Filter

from pytest import fixture

jwt_test = {'user': {'unique_id': 102030}}
params_test = Filter(**{'id': 10})


@fixture(scope='function')
def client_ticket_details_list_service():
    client_ticket_details_list_service = TicketDetailsService(
        url_path='',
        x_thebes_answer=jwt_test,
        params=params_test
    )
    return client_ticket_details_list_service
