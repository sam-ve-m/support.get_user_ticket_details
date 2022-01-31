#!/bin/bash
fission spec init
fission env create --spec --name get-user-ticket-details-env --image nexus.sigame.com.br/python-env-3.8:0.0.4 --builder nexus.sigame.com.br/python-builder-3.8:0.0.1
fission fn create --spec --name get-user-ticket-details-fn --env get-user-ticket-details-env --src "./func/*" --entrypoint main.fn
fission route create --spec --method GET --url /get_user_ticket_details --function get-user-ticket-details-fn
