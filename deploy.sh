#!/bin/bash
fission spec init
fission env create --spec --name get-ticket-details-env --image nexus.sigame.com.br/python-env-3.8:0.0.5 --builder nexus.sigame.com.br/fission-builder-3.8:0.0.1
fission fn create --spec --name get-ticket-details-fn --env get-ticket-details-env --src "./func/*" --entrypoint main.get_user_ticket_details --executortype newdeploy --maxscale 1
fission route create --spec --name get-ticket-details-rt --method GET --url /support/get-ticket-details --function get-ticket-details-fn
