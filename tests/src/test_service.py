from unittest.mock import patch
import pytest

from func.src.service import TicketDetailsService
from .conftest import StubUser, StubGetUsers, StubGroup, StubTicket, StubComment


@patch.object(TicketDetailsService, '_get_zenpy_client')
def test_get_user(mock_zenpy_client, client_ticket_details_list_service):
    mock_zenpy_client().users.return_value = StubGetUsers().append_user(StubUser(external_id=102030))
    user = client_ticket_details_list_service.get_user()

    assert isinstance(user, StubUser)
    assert user.external_id == client_ticket_details_list_service.x_thebes_answer['user']['unique_id']


@patch.object(TicketDetailsService, '_get_zenpy_client')
def test_get_user_if_zenpy_client_was_called(mock_zenpy_client, client_ticket_details_list_service):
    client_ticket_details_list_service.get_user()

    mock_zenpy_client.assert_called_once_with()


@patch.object(TicketDetailsService, '_get_zenpy_client')
def test_get_user_if_zenpy_client_users_was_called(mock_zenpy_client, client_ticket_details_list_service):
    client_ticket_details_list_service.get_user()

    mock_zenpy_client().users.assert_called_once_with(external_id=102030)


@patch.object(TicketDetailsService, '_get_zenpy_client')
def test_get_user_raises(mock_zenpy_client, client_ticket_details_list_service):
    mock_zenpy_client().users.return_value = None
    with pytest.raises(Exception, match='Bad request'):
        client_ticket_details_list_service.get_user()


@patch.object(TicketDetailsService, '_get_zenpy_client')
@patch.object(TicketDetailsService, 'get_user', return_value='user123')
def test_get_tickets(mock_get_user, mock_zenpy_client, client_ticket_details_list_service):
    mock_zenpy_client().tickets.return_value = StubTicket(requester='user123', group=StubGroup())
    mock_zenpy_client().tickets.comments.return_value = [StubComment()]
    ticket = client_ticket_details_list_service.get_ticket()

    assert isinstance(ticket, dict)
    assert ticket['subject'] == 'assunto teste'
    assert ticket['description'] == 'descrição teste'
    assert ticket['comments'][0]['id'] == '123'
    assert ticket['comments'][0]['attachments'] == []
    mock_get_user.called_once()
    mock_zenpy_client.called_once()
    mock_zenpy_client().tickets.called_once_with(requester='user123', group=StubGroup())
    mock_zenpy_client().tickets.comments.called_once()


@patch.object(TicketDetailsService, '_get_zenpy_client')
@patch.object(TicketDetailsService, 'get_user')
def test_get_ticket_if_get_user_was_called(mock_get_user, mock_zenpy_client, client_ticket_details_list_service):
    client_ticket_details_list_service.get_ticket()

    mock_get_user.assert_called_once_with()


@patch.object(TicketDetailsService, '_get_zenpy_client')
@patch.object(TicketDetailsService, 'get_user')
def test_get_ticket_if_get_zenpy_client_was_called(mock_get_user, mock_zenpy_client, client_ticket_details_list_service):
    client_ticket_details_list_service.get_ticket()

    mock_zenpy_client.assert_called_once_with()


@patch.object(TicketDetailsService, '_get_zenpy_client')
@patch.object(TicketDetailsService, 'get_user')
def test_get_ticket_if_get_zenpy_client_tickets_was_called(mock_get_user, mock_zenpy_client, client_ticket_details_list_service):
    client_ticket_details_list_service.get_ticket()

    mock_zenpy_client().tickets.assert_called_once_with(id=10)


@patch.object(TicketDetailsService, '_get_zenpy_client')
@patch.object(TicketDetailsService, 'get_user', return_value='user123')
def test_get_tickets_if_zenpy_client_tickets_comments_was_called(mock_get_user, mock_zenpy_client, client_ticket_details_list_service):
    mock_zenpy_client().tickets.return_value = StubTicket(requester='user123', group=StubGroup())
    client_ticket_details_list_service.get_ticket()

    mock_zenpy_client().tickets.comments.assert_called_once_with(ticket={
        'subject': 'assunto teste',
        'description': 'descrição teste',
        'id': None,
        'status': 'teste',
        'created_at': 'data de criação',
        'update_at': 'data de atualização',
        'group': 'lionx', 'comments': []
        }
    )


def test_obj_ticket_to_dict(client_ticket_details_list_service):
    ticket = client_ticket_details_list_service.obj_ticket_to_dict(StubTicket(group=StubGroup()))

    assert isinstance(ticket, dict)
    assert ticket['subject'] == 'assunto teste'
    assert ticket['description'] == 'descrição teste'
    assert ticket['id'] is None
    assert ticket['status'] == 'teste'
    assert ticket['created_at'] == 'data de criação'
    assert ticket['update_at'] == 'data de atualização'
    assert ticket['group'] == 'lionx'


def test_obj_ticket_to_dict_when_not_have_group_name(client_ticket_details_list_service):
    ticket = client_ticket_details_list_service.obj_ticket_to_dict(StubTicket())

    assert isinstance(ticket, dict)
    assert ticket['group'] is None


def test_add_comments_on_ticket(client_ticket_details_list_service):
    ticket = client_ticket_details_list_service.obj_ticket_to_dict(StubTicket())
    client_ticket_details_list_service.add_comments_on_ticket(ticket=ticket, comments=[StubComment()])

    assert isinstance(ticket, dict)
    assert ticket['comments'][0]['author'] == 'Nome do usuário'
    assert ticket['comments'][0]['body'] == 'corpo do comentário'
    assert ticket['comments'][0]['created_at'] == '22/03/2022'
    assert ticket['comments'][0]['attachments'] == []
