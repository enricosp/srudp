# Simplest Reliable User Datagram Protocol

This software is **high experimental** level **not** use in production.

This python3 source code is POC (Proof of Concept) to transform simple packages udp in reliable data.

## Installation

TODO: **Add installation**

## Usage

### receive. py (Server)

Application sample for test receiving packages UDP reliable.

1.Receiver arguments

- `-h` or `--help`          Help message.
- `-H` or `--bind-address`  The bind address for receive socket packages. default is "0.0.0.0" (all address).
- `-p` or `--port`          The port for receive socket packages. Valid values in range 10001 to 11000.
- `-v` or `--verbose`       Enable log debug.

2.Command to test

Open terminal and run:

```bash
python3 receiver.py -H 127.0.0.1 -p 10001 -v
```

### sender. py (Client)

Application sample for test sending packages UDP reliable.

1.Sender arguments

- `-h` or `--help`          Help message.
- `-H` or `--host`          The address or host to send packages.
- `-p` or `--port`          The port to send packages. Valid values in range 10001 to 11000.
- `-n` or `--number-of-msg` The number of messages to create.
- `-v` or `--verbose`       Enable log debug.

2.Command to test

Open terminal and run:

```bash
python3 sender.py -H 127.0.0.1 -p 10001 -n 50 -v
```

>Note: Run first receiver.py

### SRUDPServer

```python
from srudp import SRUDPServer
server = SRUDPServer("0.0.0.0", 60000)

for data in server.receive():
    print ("RECV: ", data)

```

### SRUDPClient

```python
from srudp import SRUDPClient
client = SRUDPClient(host, port)
client.send(["Frame1","Frame2"])
```

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## History

Version 0.1 (2020-02-25) - Create first POC

## Credits

Enrico Spinetta (@enricosp)

## License

See <https://github.com/enricosp/srudp/blob/master/LICENSE>
