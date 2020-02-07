ipcam
=====
A Python server which captures streaming video from IP cameras.

Configuration
-------------
The server is configured with JSON file containing an array of cameras.
Each camera is configured with the following values.

```
archive: -> string  # The absolute path to the directory where the
                    # captured images will be stored.
id: -> number       # An arbitrary (unique) identification value.
url: -> string      # The url of the camera's stream.
sleep: -> number    # The approximate number of seconds between each
                    # frame capture.
start: -> string    # Time to start capturing images (HH:MM, UTC)
                    # Example: "22:30"
stop: -> string     # Time to stop capturing images (HH:MM, UTC)
                    # Example: "23:00"
```

Example configuration in the `config/` directory.

Use
---
To run issue the following commands

### Docker/Development
```
pipenv run start-docker
```

Or

### Virtual Env
Requires a configuration file: `config/docker_config.json`.

```
pipenv run start [/path/to/config]
```

Or

### Python (System Default)

```
./src/ipcam.py --config [/path/to/config]
```

