from func.src.domain.validator import TicketDetails


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


stub_unique_id = "102030"
stub_ticket_details_validated = TicketDetails(**{'id': 10}).dict()
