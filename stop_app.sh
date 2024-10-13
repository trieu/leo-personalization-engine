#!/bin/sh

kill -15 $(pgrep -f "uvicorn main:api_personalization")
sleep 2