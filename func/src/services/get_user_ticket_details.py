# Jormungandr
from ..domain.exceptions import InvalidUniqueId, TicketNotFound, InvalidTicketRequester

# Standards
from typing import List

# Third party
from decouple import config
from etria_logger import Gladsheim
from zenpy import Zenpy
from zenpy.lib.api_objects import User, Ticket, Comment, Attachment


class TicketDetailsService:
    zenpy_client = None

    def __init__(self, ticket_details_validated: dict, unique_id: str):
        self.ticket_details = ticket_details_validated
        self.unique_id = unique_id

    @classmethod
    def _get_zenpy_client(cls):
        if cls.zenpy_client is None:
            try:
                cls.zenpy_client = Zenpy(
                    **{
                        "email": config("ZENDESK_EMAIL"),
                        "password": config("ZENDESK_PASSWORD"),
                        "subdomain": config("ZENDESK_SUBDOMAIN"),
                    }
                )
            except Exception as ex:
                message = "_get_zenpy_client::error to get Zenpy Client"
                Gladsheim.error(error=ex, message=message)
                raise ex
        return cls.zenpy_client

    def _get_user(self) -> User:
        zenpy_client = self._get_zenpy_client()
        user_result = zenpy_client.users(external_id=self.unique_id)
        if user_result:
            user_zenpy = user_result.values[0]
            return user_zenpy
        message = (
            f"get_user::There is no user with this unique id specified"
            f"::{self.unique_id}"
        )
        Gladsheim.error(message=message)
        raise InvalidUniqueId

    def _get_ticket(self) -> Ticket:
        zenpy_client = self._get_zenpy_client()
        try:
            ticket_zenpy = zenpy_client.tickets(id=self.ticket_details['id'])
            return ticket_zenpy
        except Exception as ex:
            message = f'get_ticket::There is no ticket with this id {self.ticket_details["id"]}'
            Gladsheim.info(message=message, error=ex)
            raise TicketNotFound

    def get_ticket_details(self) -> dict:
        zenpy_client = self._get_zenpy_client()
        self._requester_is_the_same_ticket_user()
        ticket_id = self.ticket_details['id']
        ticket_zenpy = zenpy_client.tickets(id=ticket_id)
        ticket = self._obj_ticket_to_dict(ticket_zenpy)
        comments = zenpy_client.tickets.comments(ticket=ticket_zenpy)
        treated_ticket = self._add_comments_on_ticket(ticket=ticket, comments=comments)
        result = {"ticket": treated_ticket}
        return result

    def _requester_is_the_same_ticket_user(self) -> bool:
        user_zenpy = self._get_user()
        ticket_zenpy = self._get_ticket()
        if ticket_zenpy.requester == user_zenpy:
            return True
        message = (
            f"requester_is_the_same_ticket_user::Requester is not the ticket owner::"
            f"Requester:{ticket_zenpy.requester}::Ticket owner user:{user_zenpy}"
        )
        Gladsheim.info(message=message)
        raise InvalidTicketRequester

    @staticmethod
    def _unpack_attachments(attachments) -> List[Attachment]:
        attachment_list = [{
            'name': attachment.file_name,
            'url': attachment.content_url,
            'content_type': attachment.content_type,
        } for attachment in attachments]
        return attachment_list

    def _add_comments_on_ticket(self, ticket: dict, comments: List[Comment]) -> dict:
        comments_normalized = list()
        for comment in comments:
            if comment.public:
                attachments = self._unpack_attachments(comment.attachments)
                comment = {
                        'id': comment.id,
                        'author': comment.author.name,
                        'created_at': comment.created,
                        'body': comment.body,
                        'attachments': attachments
                }
                comments_normalized.append(comment)
        ticket.update({'comments': comments_normalized})
        return ticket

    @staticmethod
    def _obj_ticket_to_dict(ticket: Ticket) -> dict:
        group_name = ticket.group.name if ticket.group else None
        ticket_details = {
            'subject': ticket.subject,
            'description': ticket.description,
            'id': ticket.id,
            'status': ticket.status,
            'created_at': ticket.created,
            'update_at': ticket.updated,
            'group': group_name,
        }
        return ticket_details
