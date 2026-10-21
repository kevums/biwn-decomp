"""Private local IPC for LM Studio's existing scoped evidence helper.

Start from the workbench/Terminal, which can read the project directory.
No network listener, model inference, arbitrary commands, or weight changes.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import selectors
import socket
import socketserver
import subprocess
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path.home() / '.lmstudio/local-ai-lab'
SOCKET = RUNTIME / 'runs/native-evidence-v1.sock'
LIMIT = 2 * 1024 * 1024
WRITE_LOCK = threading.Lock()


def record(event, **fields):
    with WRITE_LOCK:
        with (RUNTIME / 'runs/native-evidence-broker-v1.jsonl').open('a') as f:
            f.write(json.dumps(dict(time=datetime.now(timezone.utc).isoformat(), event=event, **fields)) + '\n')


def ping():
    try:
        with socket.socket(socket.AF_UNIX) as s:
            s.settimeout(2)
            s.connect(str(SOCKET))
            s.sendall(b'{"op":"ping"}\n')
            return json.loads(s.makefile('rb').readline(LIMIT)).get('status') == 'ready'
    except (OSError, ValueError):
        return False


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        child = None
        try:
            self.connection.settimeout(900)
            raw = self.rfile.readline(LIMIT + 1)
            if len(raw) > LIMIT or not raw.endswith(b'\n'):
                raise ValueError('Request exceeds the local transport limit.')
            request = json.loads(raw)
            if request.get('op') == 'ping':
                self.wfile.write(b'{"status":"ready","protocol":1}\n')
                return
            mode = request.get('mode')
            payload = request.get('payload')
            if mode not in ['context', 'validate'] or not isinstance(payload, dict):
                raise ValueError('Unknown scoped request.')
            if mode == 'context' and (payload.get('domain') not in ['game', 'advertising'] or not isinstance(payload.get('query'), str)):
                raise ValueError('Expected a game or advertising text query.')
            command = [str(RUNTIME / '.venv/bin/python3.12'), str(ROOT / 'scripts/native_chat_team_context.py')]
            if mode == 'validate':
                command.append('--validate-advertising-brief')
            # Fixed command; request text is only JSON on stdin.
            with tempfile.TemporaryFile() as errors:
                child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors, cwd='/')
                record('helper_started', pid=child.pid, mode=mode, query=payload.get('query'))
                child.stdin.write(json.dumps(payload).encode() + b'\n')
                child.stdin.flush()
                with selectors.DefaultSelector() as selector:
                    selector.register(child.stdout, selectors.EVENT_READ)
                    if not selector.select(25):
                        raise TimeoutError('Workbench evidence lookup timed out.')
                    response = child.stdout.readline(LIMIT + 1)
                if len(response) > LIMIT or not response.endswith(b'\n'):
                    errors.seek(0)
                    raise ValueError('Evidence helper failed: ' + errors.read(2000).decode(errors='replace'))
                json.loads(response)
                self.wfile.write(response)
                self.wfile.flush()
                # Context helper retains the existing inference lock for the
                # entire team turn. Bridge EOF releases it; validation exits.
                if mode == 'context':
                    while self.rfile.read(1):
                        pass
                record('lease_closed', pid=child.pid, mode=mode)
        except (OSError, ValueError, TimeoutError) as error:
            record('request_failed', error=str(error))
            try:
                self.wfile.write(json.dumps(dict(status='failed', message=str(error))).encode() + b'\n')
            except OSError:
                pass
        finally:
            if child:
                try:
                    child.stdin.close()
                    child.wait(timeout=3)
                except (OSError, subprocess.TimeoutExpired):
                    child.terminate()
                    try:
                        child.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait()


class Server(socketserver.ThreadingUnixStreamServer):
    daemon_threads = True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ensure', action='store_true')
    args = ap.parse_args()
    SOCKET.parent.mkdir(exist_ok=True, parents=True)
    if ping():
        print('Local evidence bridge is ready.', flush=True)
        return
    if args.ensure:
        log = (RUNTIME / 'runs/native-evidence-broker-launcher.log').open('a')
        process = subprocess.Popen(['/usr/bin/python3', str(Path(__file__).resolve())], cwd='/', stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
        import time
        for _ in range(50):
            if ping():
                print('Local evidence bridge ready (PID ' + str(process.pid) + ').', flush=True)
                return
            if process.poll() is not None:
                raise RuntimeError('Evidence bridge startup failed; inspect native-evidence-broker-launcher.log.')
            time.sleep(.1)
        raise TimeoutError('Evidence bridge did not become ready.')
    # A stale socket is an endpoint, not evidence of a live process.
    if SOCKET.exists():
        SOCKET.unlink()
    old_umask = os.umask(0o177)
    try:
        with Server(str(SOCKET), Handler) as server:
            os.chmod(SOCKET, 0o600)
            record('server_started', pid=os.getpid(), source_root=str(ROOT), socket_mode='0600')
            print('Private local evidence bridge ready: ' + str(SOCKET), flush=True)
            try:
                server.serve_forever()
            finally:
                SOCKET.unlink(missing_ok=True)
    finally:
        os.umask(old_umask)


if __name__ == '__main__':
    main()
