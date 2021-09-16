# Mosaic Server

Small webserver used for WebRTC Signalling by [Mosaic](https://github.com/winston-yallow/mosaic-client).
This was done for a game jam with limited time and probably contains bugs.

I planned to make this into a module and creating a setup.py but ran out of time. For now the
main entry point is the `cli.py` file.

## Usage

### Requirements
I suggest using a virtual environment. You can create one and install the dependencies like this on linux:

```bash
python3 -m venv venv
pip install -r requirements.txt
```

### Running the Server

(if you followed the steps above you need to activate the environment with `source venv/bin/activate`)

Example commands:
```bash
# Print help
python src/cli.py --help

# Start server and print info messages
python src/cli.py --loglevel INFO

# Start server with SSL support
python src/cli.py \
    --cert path/to/fullchain.pem \
    --key path/to/privkey.pem
```

## License
All code in this repo is using the MIT License

