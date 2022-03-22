from func.src.service import TicketDetailsService
from func.src.validator import Filter

from pytest import fixture

jwt_test = {'user': {'unique_id': 102030}}
params_test = Filter(**{'id': 10})


class Author:
    def __init__(self, name=None):
        self.name = name


class StubComment:
    def __init__(self, attachments=None):
        self.id = '123'
        self.author = Author(name='Nome do usuário')
        self.created = '22/03/2022'
        self.body = 'corpo do comentário'
        self.attachments = attachments or []
        self.public = True


class StubUser:
    def __init__(self, id=None, external_id=None):
        self.id = id or None
        self.external_id = external_id or None


class StubGetUsers:
    def __init__(self, values=None):
        self.values = values or []

    def append_user(self, stub_user: StubUser):
        self.values.append(stub_user)
        return self


class StubGroup:
    def __init__(self, name=None):
        self.name = name or 'lionx'


class StubTicket:
    def __init__(self, comment=None, requester=None, id=None, subject=None, status=None, created=None, description=None, updated=None, group=None):
        self.comment = comment or None
        self.requester = requester or None
        self.id = id or None
        self.subject = subject or 'assunto teste'
        self.description = description or 'descrição teste'
        self.status = status or 'teste'
        self.created = created or 'data de criação'
        self.updated = updated or 'data de atualização'
        self.group = group or None


@fixture(scope='function')
def client_ticket_details_list_service():
    client_ticket_details_list_service = TicketDetailsService(
        url_path='',
        x_thebes_answer=jwt_test,
        params=params_test
    )
    return client_ticket_details_list_service
