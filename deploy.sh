#!/bin/bash
fission spec init
fission env create --spec --name get-user-ticket-details-env --image fission/python-env-3.8 --builder fission/python-builder-3.8
fission fn create --spec --name get-user-ticket-details-fn --env get-user-ticket-details-env --src "./func/*" --entrypoint main.fn
fission route create --spec --method POST --url /post_user_ticket --function get-user-ticket-details-fn
