# Standards
from typing import Optional, List
import os

# Third part
from decouple import Config, RepositoryEnv, config
from nidavellir import Sindri
from pydantic import BaseModel
from zenpy import Zenpy
from zenpy.lib.api_objects import User, Ticket, Comment

# path = os.path.join("/", "app", ".env")
# path = str(path)
# config = Config(RepositoryEnv(path))


class TicketDetailsService:
    zenpy_client = None

    @classmethod
    def _get_zenpy_client(cls):
        if cls.zenpy_client is None:
            cls.zenpy_client = Zenpy(**{
                'email': config('ZENDESK_EMAIL'),
                'password': config('ZENDESK_PASSWORD'),
                'subdomain': config('ZENDESK_SUBDOMAIN')
            })
        return cls.zenpy_client

    def __init__(self, params: BaseModel, url_path: str, x_thebes_answer: dict):
        self.params = params.dict()
        Sindri.dict_to_primitive_types(self.params)
        self.url_path = url_path
        self.x_thebes_answer = x_thebes_answer

    def get_tickets(self) -> dict:
        ticket = {}
        user = self.get_user()
        ticket = self.zenpy_client.tickets(id=self.params['id'])
        if ticket.requester == user:
            ticket = self.obj_ticket_to_dict(ticket)
            comments = self.zenpy_client.tickets.comments(ticket=ticket)
            self.add_comments_on_ticket(ticket=ticket, comments=comments)
        return ticket

    @staticmethod
    def add_comments_on_ticket(ticket: dict, comments: List[Comment]):
        comments_normalized = list()
        for comment in comments:
            if comment.public:
                comments_normalized.append({
                    "id": comment.id,
                    "author": comment.author.name,
                    "created_at": comment.created,
                    "body": comment.body,
                    "attachments": [
                        {
                            "name": attachment.file_name,
                            "url": attachment.content_url,
                            "content_type": attachment.content_type
                        }
                        for attachment in comment.attachments
                    ]
                })
        ticket.update({"comments": comments_normalized})

    @staticmethod
    def obj_ticket_to_dict(ticket: Ticket) -> dict:
        group_name = None
        if ticket.group:
            group_name = ticket.group.name
        return {
            "subject": ticket.subject,
            "description": ticket.description,
            "id": ticket.id,
            "status": ticket.status,
            "created_at": ticket.created,
            "update_at": ticket.updated,
            "group": group_name
        }

    def get_user(self) -> User:
        unique_id = self.x_thebes_answer['user']['unique_id']
        zenpy_client = self._get_zenpy_client()
        if user_results := zenpy_client.users(external_id=unique_id):
            user_obj = user_results.values[0]
            return user_obj
        raise Exception('Bad request')
