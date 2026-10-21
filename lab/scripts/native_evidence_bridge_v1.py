"""Relay one scoped evidence request through the private workbench socket."""
import json
from pathlib import Path
import socket
import sys


def main():
    mode = 'validate' if sys.argv[1:] == ['--validate-advertising-brief'] else 'context'
    request = json.loads(sys.stdin.readline())
    path = Path.home() / '.lmstudio/local-ai-lab/runs/native-evidence-v1.sock'
    try:
        with socket.socket(socket.AF_UNIX) as connection:
            connection.settimeout(28)
            connection.connect(str(path))
            connection.sendall(json.dumps(dict(mode=mode, payload=request)).encode() + b'\n')
            response = connection.makefile('rb').readline(2 * 1024 * 1024 + 1)
            if not response.endswith(b'\n'):
                raise ValueError('Incomplete evidence bridge response.')
            result = json.loads(response)
            print(json.dumps(result), flush=True)
            if mode == 'context' and result.get('status') == 'ready':
                sys.stdin.read()
    except (OSError, ValueError) as error:
        print(json.dumps(dict(status='failed', message='Open Start Local Evidence Bridge.command from the workbench, then retry Chat. ' + str(error))), flush=True)


if __name__ == '__main__':
    main()
