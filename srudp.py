#
# srudp.py
#
# Simplest Reliable User Datagram Protocol : https://github.com/enricosp/srudp
#
# By Enrico Spinetta
# License: MIT
#   See https://github.com/enricosp/srudp/blob/master/LICENSE
#
from zlib import crc32
from socket import socket, AF_INET, SOCK_DGRAM, error as socket_error, timeout as socket_timeout
from struct import unpack_from, pack, calcsize, error as struct_error
from enum import IntEnum
import logging

class MessageType(IntEnum):
    """
        Enumerator of type of messages
    """
    NONE=-1
    DATA_SEQ_0=0
    DATA_SEQ_1=1
    ACK_SEQ_0=2
    ACK_SEQ_1=3
    PONG=0xFE
    PING=0xFF

class Message():
    FORMAT_HEADER='!BII'
    FORMAT_CRC='!L'
    __slots__ = ('_msg_type', 'msg_num', 'msg_total', 'data', 'crc', 'is_valid')

    def __init__(self, msg_type=MessageType.NONE, msg_num=0, msg_total=0, data=b''):
        """
            Init class Message
        """
        self._msg_type = msg_type
        self.msg_num = msg_num
        self.msg_total = msg_total
        self.data = data
        self.crc = None
        self.is_valid = None

    def unpack(self, datagram):
        """
            Unpack datagram message
        """
        header_size=calcsize(Message.FORMAT_HEADER)
        crc_size=calcsize(Message.FORMAT_CRC)
        self.msg_type, self.msg_num, self.msg_total = unpack_from(Message.FORMAT_HEADER, datagram, 0)
        self.crc, = unpack_from(Message.FORMAT_CRC, datagram, len(datagram) - crc_size)
        self.data=datagram[header_size:len(datagram)-crc_size]
        self.is_valid=self.crc == crc32(datagram[0:len(datagram)-crc_size])

    def clear_data(self):
        """
            Clear data and crc
        """
        self.data = b''
        self.crc = None
        self.is_valid = False

    @property
    def msg_type(self):
        """
            Get message type
        """
        return self._msg_type

    @msg_type.setter
    def msg_type(self, msg_type):
        """
            Set message type and clear data if not data type
        """
        self._msg_type = MessageType(msg_type)
        self.crc = None
        if self._msg_type == MessageType.ACK_SEQ_0 or self._msg_type == MessageType.ACK_SEQ_1:
           self.clear_data()

    @property
    def datagram(self):
        """
            Datagram of message
        """
        data=pack(Message.FORMAT_HEADER, int(self._msg_type), self.msg_num, self.msg_total)
        data+=self.data.encode() if isinstance(self.data, str) else self.data
        if self.crc == None:
            self.crc = crc32(data)
        data+=pack(Message.FORMAT_CRC, self.crc)
        return data

class SRUDPClient:
    def __init__(self, host, port):
        """
            Simplest Reliable User Datagram Protocol - Client
            Parameters:
                host (str): Hostname or IP to transmit
                port (int): Number of port to listening
        """

        self._logger = logging.getLogger(self.__class__.__name__)
        self._client = socket(AF_INET, SOCK_DGRAM)
        self._client.settimeout(1)
        self._address = (host, port)

    def close(self):
        """
            Close socket
        """
        self._client.close()

    def _sendmsg(self, msg):
        """
            Send msg to server, return True if successful
        """
        try:
            self._client.sendto(msg.datagram, self._address)
        except socket_error as error:
            self._logger.exception(f"Fail to send: {error}")
            return False
        return True

    def _receivemsg(self):
        """
            Receive msg from server, timeout is configured on __init__
        """
        msg = Message()
        try:
            data, address = self._client.recvfrom(2048)
            if (address != self._address):
                self._logger.debug(f"Address differ {address} != {self._address}")
            msg.unpack(data)
        except socket_timeout:
            self._logger.debug(f"Timeout from {self._address}")
            msg = None
        except socket_error as error:
            self._logger.exception(f"Fail receive from {self._address}: {error}")
            msg = False
        return msg

    def ping(self, tries, data):
        """
            Try ping to server, if one packed receive pong return True
        """
        for attempt in range(0, tries):
            msg = Message(msg_type=MessageType.PING, msg_num=attempt+1, msg_total=tries, data=data)
            if not self._sendmsg(msg):
                continue
            response = self._receivemsg()
            if response and response.is_valid and response.data == msg.data and response.msg_type == MessageType.PONG:
                return True
        return False

    def send(self, data):
        """
            Send data to server
        """
        msg_total = len(data)
        for i, d in enumerate(data):
            msg = Message(msg_type=MessageType.DATA_SEQ_0 if i % 2 == 0 else MessageType.DATA_SEQ_1, msg_num=i+1, msg_total=msg_total, data= d)
            need_send=True
            while True:
                if need_send:
                    self._logger.info(f"SENT: {msg.data}")
                    self._logger.debug(f"Send message: {msg.msg_num}/{msg.msg_total}  {msg.msg_type.name} -  {msg.data}")
                    self._sendmsg(msg)

                need_send = True
                response_msg = self._receivemsg()
                if response_msg == None:
                    self._logger.info("RECV: timeout")
                    self._logger.info("")
                elif not response_msg.is_valid:
                    self._logger.error(f"Response is invalid crc={response_msg.crc:#010x}")
                elif (msg.msg_type == MessageType.DATA_SEQ_0 and response_msg.msg_type == MessageType.ACK_SEQ_1) or (msg.msg_type == MessageType.DATA_SEQ_1 and response_msg.msg_type == MessageType.ACK_SEQ_0):
                    need_send = False
                    self._logger.error(f"Receive wrong ack")
                elif response_msg.msg_num != msg.msg_num:
                    self._logger.error(f"Response wrong order, num={response_msg.msg_num} expect {msg.msg_num}")
                else:
                    self._logger.info("RECV: ACK")
                    self._logger.info("")
                    self._logger.debug(f"Response message: {response_msg.msg_num}/{response_msg.msg_total}  {response_msg.msg_type.name} -  {response_msg.data}")
                    break

class SRUDPServer:
    def __init__(self, bind_address, server_port):
        """
            Simplest Reliable User Datagram Protocol - Server
            Parameters:
                bind_address (str): Bind address
                server_port  (int): Number of port to listening
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._server = socket(AF_INET, SOCK_DGRAM)
        self._server.bind((bind_address, server_port))
        pass

    def close(self):
        """
            Close socket
        """
        self._server.close()

    def receive(self):
        """
            Return sequence of valid data
        """
        self.last_response=Message(msg_type=MessageType.ACK_SEQ_1)

        is_end = False
        while not is_end:
            message, client_address = self._server.recvfrom(2048)
            self._logger.info("RECV: message received.")
            self._logger.debug(f"Receive LEN={len(message)} bytes")
            is_end, response, data = self.process(message)
            self._server.sendto(response, client_address)
            self._logger.info("SENT: message sended.")
            self._logger.debug(f"Send    LEN={len(response)} bytes")
            if data:
                yield data

    def process(self, data_message):
        """
            Process raw of messsage and return raw of response.
        """
        is_end = False
        data = None
        msg=None

        try:
            msg = Message()
            msg.unpack(data_message)
        except struct_error as error:
            self._logger.error(f"Fail to unpack {error}")

        if (msg and msg.msg_type == MessageType.PING):
            self._logger.debug(f"Receive ping {msg.msg_num}/{msg.msg_total} - [{msg.data}] and Response PONG")
            msg.msg_type = MessageType.PONG
            return (is_end, msg.datagram, data)

        is_valid = msg and msg.is_valid and ((msg.msg_type == MessageType.DATA_SEQ_0 and self.last_response.msg_type == MessageType.ACK_SEQ_1) or
                                             (msg.msg_type == MessageType.DATA_SEQ_1 and self.last_response.msg_type == MessageType.ACK_SEQ_0))

        if is_valid:
            is_end = not msg.msg_num < msg.msg_total
            self._logger.debug(f"Receive  message: {msg.msg_num}/{msg.msg_total} ({msg.msg_type.name}) - [{msg.data}] end={is_end}")
            data = msg.data
            msg.msg_type = MessageType.ACK_SEQ_0 if msg.msg_type == MessageType.DATA_SEQ_0 else MessageType.ACK_SEQ_1
            self.last_response = msg
        else:
            self._logger.debug("Receive invalid message")

        self._logger.debug(f"Response message: {self.last_response.msg_num}/{self.last_response.msg_total}  {self.last_response.msg_type.name} - {self.last_response.data}")
        return (is_end, self.last_response.datagram, data)