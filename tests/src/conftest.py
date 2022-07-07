# Jormungandr
from func.src.services.get_user_ticket_details import TicketDetailsService
from .stubs import stub_unique_id, stub_ticket_details_validated
# Third party
from pytest import fixture


@fixture(scope='function')
def client_ticket_details_list_service():
    client_ticket_details_list_service = TicketDetailsService(
        unique_id=stub_unique_id,
        ticket_details_validated=stub_ticket_details_validated
    )
    return client_ticket_details_list_service
