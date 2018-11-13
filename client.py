import asyncio
import common
import logging
import argparse
import time

class EchoClientProtocol(common.Handler):
    """
    Defines a echo client protocol
    """

    def __init__(self, loop, name):
        """
        Class constructor

        :param name: client's name
        :param loop: asyncio loop
        """
        super().__init__()
        self.loop = loop
        self.name = name
        self.stop_event = asyncio.Event(loop=self.loop)


    def connection_made(self, transport):
        """
        Defines process of connecting to the server

        :param transport: socket to write data on
        """
        self.transport = transport
        asyncio.gather(self.send_request(command='hello', data=self.name))
        logging.info('Data sent: {!r}'.format('Hello world!'))


    def connection_lost(self, exc):
        """
        Defines process of closing connection with the server

        :param exc:
        :return:
        """
        logging.info('The server closed the connection')
        logging.info('Stopping tasks')
        self.stop_event.set()
        for task in asyncio.Task.all_tasks():
            task.cancel()
        logging.info('Stop the event loop')


    def process_response(self, command, payload):
        """
        Defines response commands for clients

        :param command: response command received
        :param payload: data received
        :return:
        """
        if command == 'ok-m':
            return "Sucessful response from master: {}".format(payload)
        else:
            return super().process_response(command, payload)


    def process_request(self, command, data):
        """
        Defines commands for clients

        :param command: Received command from client.
        :param data: Received data from client.
        :return: message to send
        """
        if command == "echo-m":
            return self.echo_client(data)
        else:
            return super().process_request(command, data)


    def echo_client(self, data):
        return 'ok-c', data


    @asyncio.coroutine
    async def client_echo(self):
        while not self.stop_event.is_set():
            result = await self.send_request('echo-c','hello from client')
            logging.info(result)
            await asyncio.sleep(3)


try:
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', help="Client's name", type=str, dest='name', required=True)
    args = parser.parse_args()

    loop = asyncio.get_event_loop()

    while True:
        try:
            coro = loop.create_connection(lambda: EchoClientProtocol(loop, args.name), '127.0.0.1', 8888)
            _, client_obj = loop.run_until_complete(coro)
        except ConnectionRefusedError:
            logging.error("Could not connect to server. Trying again in 10 seconds.")
            time.sleep(10)
            break

        try:
            loop.run_until_complete(client_obj.client_echo())
            loop.run_forever()
        except asyncio.CancelledError:
            logging.debug("Lost connection with server. Reconnecting in 10 seconds.")
            time.sleep(10)

    loop.close()

except KeyboardInterrupt:
    logging.info("Closing connection.")
