#!/bin/bash

sleep 15
while ! nc -z $mongo_host $mongo_port; do
      echo "Установка соединения с Mongo $mongo_host $mongo_port"
      sleep 2
done 

exec "$@"