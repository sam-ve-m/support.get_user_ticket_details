from typing import List

from decouple import config
from nidavellir import Sindri
from pydantic import BaseModel
from zenpy import Zenpy
from zenpy.lib.api_objects import User, Ticket, Comment, Attachment


class TicketDetailsService:
    zenpy_client = None

    @classmethod
    def _get_zenpy_client(cls):
        if cls.zenpy_client is None:
            cls.zenpy_client = Zenpy(
                **{
                    'email': config('ZENDESK_EMAIL'),
                    'password': config('ZENDESK_PASSWORD'),
                    'subdomain': config('ZENDESK_SUBDOMAIN'),
                }
            )
        return cls.zenpy_client

    def __init__(
        self, params: BaseModel, url_path: str, x_thebes_answer: dict
    ):
        self.params = params.dict()
        Sindri.dict_to_primitive_types(self.params)
        self.url_path = url_path
        self.x_thebes_answer = x_thebes_answer

    def get_user(self) -> User:
        unique_id = self.x_thebes_answer['user']['unique_id']
        zenpy_client = self._get_zenpy_client()
        if user_results := zenpy_client.users(external_id=unique_id):
            user_obj = user_results.values[0]
            return user_obj
        raise Exception('Bad request')

    def get_ticket(self) -> dict:
        user = self.get_user()
        zenpy_client = self._get_zenpy_client()
        ticket = zenpy_client.tickets(id=self.params['id'])
        if ticket.requester == user:
            ticket = self._obj_ticket_to_dict(ticket)
            comments = zenpy_client.tickets.comments(ticket=ticket)
            ticket = self._add_comments_on_ticket(ticket=ticket, comments=comments)
        return ticket

    @staticmethod
    def _unpack_attachments(attachments) -> List[Attachment]:
        attachment_list = [{
            'name': attachment.file_name,
            'url': attachment.content_url,
            'content_type': attachment.content_type,
        } for attachment in attachments]
        return attachment_list

    @staticmethod
    def _add_comments_on_ticket(ticket: dict, comments: List[Comment]) -> dict:
        comments_normalized = list()
        for comment in comments:
            if comment.public:
                attachments = TicketDetailsService._unpack_attachments(comment.attachments)
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
        group_name = None
        if ticket.group:
            group_name = ticket.group.name
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
        return ticket
