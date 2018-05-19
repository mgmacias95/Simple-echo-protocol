# Simple-echo-protocol

Simple echo server and client made with asyncio.

This code will be used as example for my talk at the [__YWT On The Beach__ meetup](https://www.meetup.com/es-ES/yeswetech/events/250109575/)

## How to use
The defined file structure allows implementing new messages for the protocol. Edit `process_request` and `process_response` functions:
  * In `common.py` file to add requests and responses for both server and client.
  * In `server.py` file to add requests and responses for the server.
  * In `client.py` file to add requests and responses for clients.
