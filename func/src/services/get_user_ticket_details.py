# Jormungandr
from ..domain.exceptions import InvalidUniqueId, TicketNotFound, InvalidTicketRequester

# Standards
from typing import List

# Third party
from decouple import config
from etria_logger import Gladsheim
from nidavellir import Sindri
from pydantic import BaseModel
from zenpy import Zenpy
from zenpy.lib.api_objects import User, Ticket, Comment, Attachment


class TicketDetailsService:
    zenpy_client = None

    def __init__(
        self, params: BaseModel, url_path: str, decoded_jwt: dict
    ):
        self.params = params.dict()
        Sindri.dict_to_primitive_types(self.params)
        self.url_path = url_path
        self.decoded_jwt = decoded_jwt

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
        unique_id = self.decoded_jwt["user"]["unique_id"]
        zenpy_client = self._get_zenpy_client()
        user_result = zenpy_client.users(external_id=unique_id)
        if user_result:
            user_zenpy = user_result.values[0]
            return user_zenpy
        message = (
            f"get_user::There is no user with this unique id specified"
            f"::{self.decoded_jwt['user']['unique_id']}"
        )
        Gladsheim.error(message=message)
        raise InvalidUniqueId

    def _get_ticket(self) -> Ticket:
        zenpy_client = self._get_zenpy_client()
        ticket_zenpy = zenpy_client.tickets(id=self.params['id'])
        return ticket_zenpy

    def get_ticket_details(self) -> dict:
        zenpy_client = self._get_zenpy_client()
        self._requester_is_the_same_ticket_user()
        try:
            ticket_zenpy = zenpy_client.tickets(id=self.params['id'])
            ticket = self._obj_ticket_to_dict(ticket_zenpy)
            comments = zenpy_client.tickets.comments(ticket=ticket)
            treated_ticket = self._add_comments_on_ticket(ticket=ticket, comments=comments)
            return treated_ticket
        except Exception as ex:
            message = f'get_ticket::There is no ticket with this id {self.params["id"]}'
            Gladsheim.error(message=message, error=ex)
            raise TicketNotFound

    def _requester_is_the_same_ticket_user(self) -> bool:
        user_zenpy = self._get_user()
        ticket_zenpy = self._get_ticket()
        if ticket_zenpy.requester == user_zenpy:
            return True
        message = (
            f"requester_is_the_same_ticket_user::Requester is not the ticket owner::"
            f"Requester:{ticket_zenpy.requester}::Ticket owner user:{user_zenpy}"
        )
        Gladsheim.error(message=message)
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
