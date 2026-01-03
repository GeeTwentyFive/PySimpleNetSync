Python client library for [SimpleNetSyncServer](https://github.com/GeeTwentyFive/SimpleNetSyncServer)


# Install

`pip install .`


# Usage example

```py
from SimpleNetSync import SimpleNetSync
from time import sleep


local_client_state = 0


sns = SimpleNetSync("::1", 55555)
print(f"Local ID: {sns.local_id}")
while True:
        print(sns.states)
        local_client_state += 1
        sns.send(str(local_client_state))
        sleep(0.1)
```


# API

- Constructor: `sns = SimpleNetSync(server_ip, server_port)`
- State of all clients (as `{int: str}` dictionary, where `int` is client ID, and `str` is state): `sns.state`
- Local client ID: `sns.local_id`
- Update local client's state on server: `sns.send(LOCAL_STATE)`