from pytest import fixture
from unittest.mock import patch
import json

from func.src.service import ClientTicketDetailsService
from func.src.validator import ClientAccountChange


@fixture
def get_params():
    message = {
        "cd_cliente": 1,
        "dt_lancamento": "2021-10-10",
        "dv_cliente": 9,
        "dt_referencia": "2021-10-10",
        "dt_liquidacao": "2021-10-11",
        "in_origem": "D",
        "vl_lancamento": -1500.00,
    }
    return message


def test_get_bovespa_account(get_params):
    client_account_change_service = ClientTicketDetailsService(
        params=ClientAccountChange(**get_params), url_path="/test"
    )
    bovespa_account = client_account_change_service._get_bovespa_account()
    assert len(bovespa_account) == 11
    assert bovespa_account == "000000001-9"


def test_build_kafka_message(get_params):
    client_account_change_service = ClientTicketDetailsService(
        params=ClientAccountChange(**get_params), url_path="/test"
    )
    transaction = client_account_change_service._build_kafka_message()
    assert "id" in transaction
    assert "timestamp" in transaction
    assert transaction["type"] == "transactions.created"
    assert transaction["payload"] == {
        "bovespa_account": "000000001-9",
        "release_date": 1633834800.0,
        "reference_date": 1633834800.0,
        "settlement_date": 1633921200.0,
        "transaction_type": "D",
        "price": -1500.0,
    }


class StubProducer:
    def __init__(self):
        self.sent_messages = []

    def send(self, topic, value):
        self.sent_messages.append((topic, value))

        class Confirmation:
            is_done = True

        return Confirmation


@patch.object(ClientTicketDetailsService, "_get_producer", return_value=StubProducer())
@patch.object(ClientTicketDetailsService, "_get_topic", side_effect=["test"])
def test_insert_in_queue(mock_get_producer, mock_get_topic, get_params):
    client_account_change_service = ClientTicketDetailsService(
        params=ClientAccountChange(**get_params), url_path="/test"
    )
    client_account_change_service.insert_in_queue()
    producer = client_account_change_service._get_producer()
    assert producer.sent_messages[0][0] == "test"
    assert json.loads(producer.sent_messages[0][1])
