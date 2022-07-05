# Jormungandr
from func.src.services.get_user_ticket_details import TicketDetailsService
from func.src.domain.validator import Filter

# Third party
from pytest import fixture

jwt_test = {'user': {'unique_id': 102030}}
params_test = Filter(**{'id': 10})


@fixture(scope='function')
def client_ticket_details_list_service():
    client_ticket_details_list_service = TicketDetailsService(
        url_path='',
        decoded_jwt=jwt_test,
        params=params_test
    )
    return client_ticket_details_list_service
