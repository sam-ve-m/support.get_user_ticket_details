from unittest.mock import patch
import pytest

from func.src.service import TicketDetailsService
from func.src.validator import Filter

jwt_test = {'user': {'unique_id': 102030}}
params_test = Filter(**{'id': 10})


class StubUser:
    def __init__(self):
        self.id = None
        self.external_id = None

    def set_external_id(self, external_id: int):
        self.external_id = external_id
        return self

    def set_id(self, user_id: int):
        self.id = user_id
        return self


class StubGetUsers:
    def __init__(self):
        self.values = []

    def append_user(self, stub_user: StubUser):
        self.values.append(stub_user)
        return self


@patch.object(TicketDetailsService, '_get_zenpy_client')
def test_get_user(mock_zenpy_client):
    client_ticket_list_service = TicketDetailsService(url_path='', x_thebes_answer=jwt_test, params=params_test)
    mock_zenpy_client().users.return_value = StubGetUsers().append_user(StubUser())
    user = client_ticket_list_service.get_user()

    assert isinstance(user, StubUser)
    mock_zenpy_client.assert_called()
    mock_zenpy_client().users.asser_called_once_with(external_id=102030)


@patch.object(TicketDetailsService, '_get_zenpy_client')
def test_get_user_raises(mock_zenpy_client):
    client_ticket_list_service = TicketDetailsService(url_path='', x_thebes_answer=jwt_test, params=params_test)
    mock_zenpy_client().users.return_value = None
    with pytest.raises(Exception, match='Bad request'):
        client_ticket_list_service.get_user()
