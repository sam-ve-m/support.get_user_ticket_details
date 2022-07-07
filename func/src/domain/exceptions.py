class InvalidJwtToken(Exception):
    msg = 'Failed to validate user credentials'


class InvalidUniqueId(Exception):
    msg = 'Failed to validate user credentials'


class InvalidTicketRequester(Exception):
    msg = 'Invalid ticker owner'


class TicketNotFound(Exception):
    msg = 'No tickets found'
