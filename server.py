import asyncio
import common
import logging

clients = {}

class EchoServerHandler(common.Handler):
    """
    Defines echo server protocol
    """

    def connection_made(self, transport):
        """
        Defines the process of accepting a connection

        :param transport: socket to write data on
        """
        peername = transport.get_extra_info('peername')
        logging.info('Connection from {}'.format(peername))
        self.transport = transport


    def process_request(self, command, data):
        """
        Defines commands for servers

        :param command: Received command from client.
        :param data: Received data from client.
        :return: message to send
        """
        if command == "echo-c":
            return self.echo_master(data)
        elif command == 'hello':
            return self.hello(data)
        else:
            return super().process_request(command, data)


    def echo_master(self, data):
        return 'ok-m ', data


    def hello(self, data):
        """
        Adds a client's data to global clients dictionary

        :param data: client's data -> name
        :return: successful result
        """
        global clients
        if data in clients:
            logging.error("Client {} already present".format(data))
            self.transport.close()
            return 'err', 'Client already present'
        else:
            clients[data] = self
            self.name = data
            return 'ok', 'Client {} added'.format(data)


    def process_response(self, command, payload):
        """
        Defines response commands for servers

        :param command: response command received
        :param payload: data received
        :return:
        """
        if command == 'ok-c':
            return "Sucessful response from client: {}".format(payload)
        else:
            return super().process_response(command, payload)


    def connection_lost(self, exc):
        """
        Defines process of closing connection with the server

        :param exc:
        :return:
        """
        logging.info("The client '{}' closed the connection".format(self.name))
        del clients[self.name]


@asyncio.coroutine
async def server_echo():
    while True:
        for client_name, client in clients.items():
            logging.debug("Sending echo to client {}".format(client_name))
            logging.info(await client.send_request('echo-m','hello {} from server'.format(client_name)))
        await asyncio.sleep(3)


logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)

loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(EchoServerHandler, '127.0.0.1', 8888)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
logging.info('Serving on {}'.format(server.sockets[0].getsockname()))

try:
    loop.run_until_complete(server_echo())
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()