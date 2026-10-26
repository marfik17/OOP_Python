"""HTTP client and server GUI built with the Python standard library."""
from __future__ import annotations
import json
import logging
import queue
import socket
import threading
import time
from dataclasses import dataclass
import tkinter as tk
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from tkinter import ttk, messagebox
from urllib.parse import urlsplit

logging.basicConfig(filename='http_gui.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


class HttpError(Exception):
    """Raised for malformed URLs, network failures, or malformed HTTP data."""


@dataclass(frozen=True)
class ParsedURL:
    """Normalized components of an HTTP URL."""
    scheme: str
    host: str
    port: int
    target: str
    tls: bool


class URLParser:
    """Validate and split HTTP/HTTPS URLs without third-party libraries."""
    @staticmethod
    def parse(url: str) -> ParsedURL:
        if not isinstance(url, str) or not url.strip():
            raise HttpError('URL не должен быть пустым')
        try:
            parts = urlsplit(url.strip())
            scheme = parts.scheme.lower()
            if scheme not in ('http', 'https') or not parts.hostname:
                raise HttpError('Введите корректный URL, например http://localhost:8080/')
            if parts.username is not None or parts.password is not None:
                raise HttpError('URL с логином и паролем не поддерживается')
            port = parts.port or (443 if scheme == 'https' else 80)
            if not 1 <= port <= 65535:
                raise HttpError('Порт должен быть в диапазоне 1–65535')
            target = parts.path or '/'
            if parts.query:
                target += '?' + parts.query
            if parts.fragment:
                # Фрагмент URL не передаётся HTTP-серверу.
                pass
            return ParsedURL(scheme, parts.hostname, port, target, scheme == 'https')
        except ValueError as exc:
            raise HttpError(f'Некорректный URL: {exc}') from exc


class HTTPMessage:
    """Helpers for HTTP/1.x message serialization and parsing."""
    MAX_HEADER_BYTES = 16384

    @staticmethod
    def serialize_request(method: str, target: str, headers: dict[str, str], body: bytes = b'') -> bytes:
        if not target.startswith('/') or any(c in target for c in '\r\n '):
            raise HttpError('Некорректный путь HTTP-запроса')
        if not method or not method.isalpha():
            raise HttpError('Некорректный HTTP-метод')
        lines = [f'{method.upper()} {target} HTTP/1.1']
        for key, value in headers.items():
            if not key or ':' in key or any(c in key + value for c in '\r\n'):
                raise HttpError('Некорректный HTTP-заголовок')
            lines.append(f'{key}: {value}')
        return ('\r\n'.join(lines) + '\r\n\r\n').encode('iso-8859-1') + body

    @staticmethod
    def parse_response(raw: bytes) -> tuple[int, str, dict[str, str], bytes]:
        if not isinstance(raw, (bytes, bytearray)) or b'\r\n\r\n' not in raw:
            raise HttpError('Сервер вернул некорректный HTTP-ответ')
        head, body = bytes(raw).split(b'\r\n\r\n', 1)
        if len(head) > HTTPMessage.MAX_HEADER_BYTES:
            raise HttpError('Заголовки HTTP-ответа слишком большие')
        lines = head.decode('iso-8859-1', 'replace').split('\r\n')
        status_parts = lines[0].split(' ', 2)
        if len(status_parts) < 2 or not status_parts[0].startswith('HTTP/'):
            raise HttpError('Не удалось разобрать статус ответа')
        try:
            status = int(status_parts[1])
        except ValueError as exc:
            raise HttpError('Некорректный код статуса') from exc
        if not 100 <= status <= 599:
            raise HttpError('Код статуса вне диапазона 100–599')
        reason = status_parts[2] if len(status_parts) > 2 else ''
        headers: dict[str, str] = {}
        for line in lines[1:]:
            if not line or ':' not in line or line[0] in ' \t':
                raise HttpError('Некорректный HTTP-заголовок в ответе')
            key, value = line.split(':', 1)
            headers[key.strip().lower()] = value.strip()
        transfer = headers.get('transfer-encoding', '').lower()
        if 'chunked' in transfer:
            body = HTTPMessage.decode_chunked(body)
        elif 'content-length' in headers:
            try:
                length = int(headers['content-length'])
            except ValueError as exc:
                raise HttpError('Некорректный Content-Length') from exc
            if length < 0:
                raise HttpError('Content-Length не может быть отрицательным')
            body = body[:length]
        return status, reason, headers, body

    @staticmethod
    def decode_chunked(data: bytes) -> bytes:
        output = bytearray()
        position = 0
        while True:
            end = data.find(b'\r\n', position)
            if end < 0:
                raise HttpError('Некорректное chunked-тело: отсутствует размер блока')
            size_text = data[position:end].split(b';', 1)[0].strip()
            try:
                size = int(size_text, 16)
            except ValueError as exc:
                raise HttpError('Некорректный размер chunked-блока') from exc
            position = end + 2
            if size == 0:
                return bytes(output)
            if size < 0 or position + size + 2 > len(data):
                raise HttpError('Неполный chunked-блок')
            output.extend(data[position:position + size])
            position += size
            if data[position:position + 2] != b'\r\n':
                raise HttpError('Некорректное окончание chunked-блока')
            position += 2

    @staticmethod
    def serialize_response(status: int, reason: str, headers: dict[str, str], body: bytes) -> bytes:
        normalized = {k: v for k, v in headers.items()}
        normalized.setdefault('Content-Length', str(len(body)))
        normalized.setdefault('Connection', 'close')
        head = f'HTTP/1.1 {status} {reason}\r\n' + ''.join(f'{k}: {v}\r\n' for k, v in normalized.items()) + '\r\n'
        return head.encode('iso-8859-1') + body


class Transport(ABC):
    @abstractmethod
    def exchange(self, host: str, port: int, payload: bytes, timeout: float, tls: bool = False) -> bytes:
        """Send bytes to a host and return the response bytes."""


class RequestHandler(ABC):
    @abstractmethod
    def handle(self, method: str, path: str, headers: dict[str, str], body: bytes) -> tuple[int, str, str, bytes]:
        """Return status, reason, content type, and response body."""


class SocketTransport(Transport):
    def exchange(self, host, port, payload, timeout, tls=False):
        import ssl
        try:
            with socket.create_connection((host, port), timeout=timeout) as raw:
                raw.settimeout(timeout)
                if tls:
                    with ssl.create_default_context().wrap_socket(raw, server_hostname=host) as conn:
                        conn.sendall(payload)
                        return self._read_response(conn)
                raw.sendall(payload)
                return self._read_response(raw)
        except socket.timeout as exc:
            raise TimeoutError('Время ожидания соединения истекло') from exc
        except OSError as exc:
            raise ConnectionError(str(exc)) from exc

    @staticmethod
    def _read_response(sock):
        chunks = []
        while True:
            try:
                data = sock.recv(65536)
            except socket.timeout:
                if chunks:
                    break
                raise
            if not data:
                break
            chunks.append(data)
            joined = b''.join(chunks)
            if b'\r\n\r\n' in joined:
                head, body = joined.split(b'\r\n\r\n', 1)
                length = None
                for line in head.split(b'\r\n')[1:]:
                    if line.lower().startswith(b'content-length:'):
                        try: length = int(line.split(b':', 1)[1].strip())
                        except ValueError: pass
                if length is not None and len(body) >= length:
                    break
        return b''.join(chunks)


class HttpClient:
    def __init__(self, transport: Transport | None = None, timeout=5):
        self.transport = transport or SocketTransport()
        self.set_timeout(timeout)

    def set_timeout(self, timeout: float) -> None:
        """Set socket timeout in seconds; values must be positive."""
        try:
            value = float(timeout)
        except (TypeError, ValueError) as exc:
            raise ValueError('Тайм-аут должен быть положительным числом') from exc
        if value <= 0:
            raise ValueError('Тайм-аут должен быть больше нуля')
        self.timeout = value

    def request(self, url: str, method='GET', headers=None, body=''):
        parsed = URLParser.parse(url)
        tls, port, path = parsed.tls, parsed.port, parsed.target
        hdrs = {'Host': parsed.host, 'Connection': 'close', 'User-Agent': 'StudentHttpClient/1.0'}
        for key, value in (headers or {}).items():
            if not key.strip() or any(c in key + value for c in '\r\n'):
                raise HttpError('Некорректное имя или значение заголовка')
            hdrs[key.strip()] = value.strip()
        data = body.encode('utf-8') if isinstance(body, str) else body
        if method.upper() == 'POST':
            hdrs.setdefault('Content-Type', 'text/plain; charset=utf-8')
            hdrs['Content-Length'] = str(len(data))
        request = HTTPMessage.serialize_request(method, path, hdrs, data)
        response = self.transport.exchange(parsed.host, port, request, self.timeout, tls)
        status, reason, response_headers, content = HTTPMessage.parse_response(response)
        display_headers = '\n'.join(f'{k}: {v}' for k, v in response_headers.items())
        return status, display_headers, content.decode('utf-8', 'replace')


class BasicRouter(RequestHandler):
    def handle(self, method, path, headers, body):
        path_only = path.split('?', 1)[0]
        if method == 'GET' and path_only == '/':
            return 200, 'OK', 'text/html; charset=utf-8', b'<!doctype html><html><body><h1>Hello!</h1><p>Python HTTP server works.</p></body></html>'
        if method == 'POST' and path_only == '/echo':
            return 200, 'OK', headers.get('content-type', 'text/plain'), body
        if method == 'GET' and path_only == '/time':
            data = json.dumps({'time': datetime.now(timezone.utc).isoformat()}, ensure_ascii=False).encode()
            return 200, 'OK', 'application/json; charset=utf-8', data
        if method == 'GET' and path_only == '/headers':
            data = json.dumps(headers, ensure_ascii=False, indent=2).encode()
            return 200, 'OK', 'application/json; charset=utf-8', data
        if method == 'GET' and path_only.startswith('/status/'):
            try: code = int(path_only.rsplit('/', 1)[1])
            except ValueError: code = 400
            if not 100 <= code <= 599: code = 400
            reason = {200:'OK', 201:'Created', 400:'Bad Request', 403:'Forbidden', 404:'Not Found', 418:"I'm a teapot", 500:'Internal Server Error'}.get(code, 'Custom Status')
            return code, reason, 'text/plain; charset=utf-8', f'{code} {reason}'.encode()
        return 404, 'Not Found', 'text/plain; charset=utf-8', b'404 Not Found'


class HttpServer:
    def __init__(self, port: int, log_queue: queue.Queue, handler: RequestHandler | None = None):
        self.port = port; self.log_queue = log_queue; self.handler = handler or BasicRouter()
        self._socket = None; self._thread = None; self._stop = threading.Event()

    def start(self):
        if self._thread and self._thread.is_alive(): return
        self._stop.clear()
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._socket:
            try: self._socket.close()
            except OSError: pass
        if self._thread and self._thread.is_alive(): self._thread.join(timeout=1)

    def _serve(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                self._socket = server
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(('127.0.0.1', self.port)); server.listen(20); server.settimeout(.3)
                self.log_queue.put(('state', f'Работает: 127.0.0.1:{self.port}'))
                while not self._stop.is_set():
                    try: conn, addr = server.accept()
                    except socket.timeout: continue
                    except OSError:
                        if self._stop.is_set(): break
                        raise
                    threading.Thread(target=self._client, args=(conn, addr), daemon=True).start()
        except OSError as exc:
            if not self._stop.is_set(): self.log_queue.put(('state', f'Ошибка: {exc}'))
        finally:
            self._socket = None
            self.log_queue.put(('state', 'Остановлен'))

    def _client(self, conn, addr):
        started = time.perf_counter(); method = path = '-'; status = 400
        with conn:
            conn.settimeout(3)
            try:
                raw = b''
                while b'\r\n\r\n' not in raw and len(raw) < 16384:
                    chunk = conn.recv(4096)
                    if not chunk: break
                    raw += chunk
                if len(raw) >= 16384 or b'\r\n\r\n' not in raw: raise ValueError('Bad request headers')
                head, body = raw.split(b'\r\n\r\n', 1)
                lines = head.decode('iso-8859-1').split('\r\n')
                request_line = lines[0].split()
                if len(request_line) != 3: raise ValueError('Bad request line')
                method, path, version = request_line
                if not version.startswith('HTTP/1.'): raise ValueError('Bad HTTP version')
                headers = {}
                for line in lines[1:]:
                    if ':' not in line: raise ValueError('Bad header')
                    key, value = line.split(':', 1); headers[key.strip().lower()] = value.strip()
                if headers.get('transfer-encoding', '').lower() == 'chunked':
                    while b'0\r\n\r\n' not in body and len(body) <= 2_000_000:
                        chunk = conn.recv(65536)
                        if not chunk: break
                        body += chunk
                    if len(body) > 2_000_000: raise ValueError('Body too large')
                    body = HTTPMessage.decode_chunked(body)
                else:
                    length = int(headers.get('content-length', '0'))
                    if length < 0 or length > 2_000_000: raise ValueError('Bad body size')
                    while len(body) < length:
                        chunk = conn.recv(min(65536, length-len(body)))
                        if not chunk: break
                        body += chunk
                    if len(body) < length: raise ValueError('Incomplete body')
                    body = body[:length]
                status, reason, content_type, out = self.handler.handle(method.upper(), path, headers, body)
            except (ValueError, UnicodeError, socket.timeout):
                reason, content_type, out = 'Bad Request', 'text/plain; charset=utf-8', b'400 Bad Request'; status = 400
            except Exception:
                logging.exception('Request handler failed')
                reason, content_type, out = 'Internal Server Error', 'text/plain; charset=utf-8', b'500 Internal Server Error'; status = 500
            date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
            response_head = (f'HTTP/1.1 {status} {reason}\r\nContent-Type: {content_type}\r\nContent-Length: {len(out)}\r\nDate: {date}\r\nConnection: close\r\n\r\n').encode('iso-8859-1')
            try: conn.sendall(response_head + out)
            except OSError: pass
        elapsed = (time.perf_counter()-started)*1000
        logging.info('%s %s %s %.1fms from %s', method, path, status, elapsed, addr[0])
        self.log_queue.put(('log', (datetime.now().strftime('%H:%M:%S'), method, path, status, round(elapsed, 1))))


class App:
    def __init__(self, root):
        self.root = root; self.root.title('HTTP Client & Server — Python'); self.root.geometry('950x700'); self.root.minsize(780, 560)
        self.client = HttpClient(); self.log_queue = queue.Queue(); self.server = None
        tabs = ttk.Notebook(root); tabs.pack(fill='both', expand=True, padx=10, pady=10)
        self.client_tab = ttk.Frame(tabs, padding=10); self.server_tab = ttk.Frame(tabs, padding=10)
        tabs.add(self.client_tab, text='HTTP-клиент'); tabs.add(self.server_tab, text='HTTP-сервер')
        self._build_client(); self._build_server(); self.root.after(100, self._poll_queue); self.root.protocol('WM_DELETE_WINDOW', self.close)

    def _build_client(self):
        f=self.client_tab; f.columnconfigure(1, weight=1); f.rowconfigure(5, weight=1)
        ttk.Label(f,text='URL:').grid(row=0,column=0,sticky='w',pady=4)
        self.url=tk.StringVar(value='http://127.0.0.1:8080/')
        ttk.Entry(f,textvariable=self.url).grid(row=0,column=1,sticky='ew',pady=4)
        ttk.Label(f,text='Метод:').grid(row=1,column=0,sticky='w',pady=4)
        self.method=tk.StringVar(value='GET'); method_box=ttk.Combobox(f,textvariable=self.method,values=('GET','POST'),state='readonly',width=10); method_box.grid(row=1,column=1,sticky='w')
        ttk.Label(f,text='Заголовки (один на строку: Имя: значение):').grid(row=2,column=0,columnspan=2,sticky='w',pady=(8,2))
        self.headers=tk.Text(f,height=3); self.headers.insert('1.0',''); self.headers.grid(row=3,column=0,columnspan=2,sticky='ew')
        ttk.Label(f,text='Тело запроса (для POST):').grid(row=4,column=0,columnspan=2,sticky='w',pady=(8,2))
        self.body=tk.Text(f,height=5); self.body.grid(row=5,column=0,columnspan=2,sticky='nsew')
        buttons=ttk.Frame(f); buttons.grid(row=6,column=0,columnspan=2,sticky='ew',pady=8)
        ttk.Button(buttons,text='Отправить',command=self.send_request).pack(side='left')
        ttk.Button(buttons,text='Очистить',command=self.clear_response).pack(side='left',padx=8)
        self.progress=ttk.Label(buttons,text='Готово'); self.progress.pack(side='left',padx=10)
        ttk.Label(f,text='Ответ (статус, заголовки, тело):').grid(row=7,column=0,columnspan=2,sticky='w')
        self.response=tk.Text(f,height=12,wrap='word'); self.response.grid(row=8,column=0,columnspan=2,sticky='nsew'); f.rowconfigure(8,weight=1)

    def send_request(self):
        url=self.url.get(); method=self.method.get(); body=self.body.get('1.0','end-1c'); raw_headers=self.headers.get('1.0','end-1c')
        headers={}
        try:
            for line in raw_headers.splitlines():
                if not line.strip(): continue
                if ':' not in line: raise HttpError('Заголовок должен иметь вид Имя: значение')
                k,v=line.split(':',1); headers[k.strip()]=v.strip()
        except Exception as exc:
            messagebox.showerror('Ошибка ввода',str(exc)); return
        self.progress.config(text='Отправка...'); self.response.delete('1.0','end')
        def work():
            try:
                result=self.client.request(url,method,headers,body if method=='POST' else '')
                self.log_queue.put(('response',result))
            except Exception as exc: self.log_queue.put(('error',f'{type(exc).__name__}: {exc}'))
        threading.Thread(target=work,daemon=True).start()

    def clear_response(self): self.response.delete('1.0','end'); self.progress.config(text='Готово')

    def _build_server(self):
        f=self.server_tab; f.columnconfigure(0,weight=1); f.rowconfigure(2,weight=1)
        top=ttk.Frame(f); top.grid(row=0,column=0,sticky='ew')
        ttk.Label(top,text='Порт:').pack(side='left')
        self.port=tk.StringVar(value='8080'); ttk.Entry(top,textvariable=self.port,width=8).pack(side='left',padx=5)
        ttk.Button(top,text='Запустить',command=self.start_server).pack(side='left',padx=5)
        ttk.Button(top,text='Остановить',command=self.stop_server).pack(side='left')
        ttk.Button(top,text='Открыть в браузере',command=self.open_browser).pack(side='left',padx=5)
        self.state=ttk.Label(f,text='● Остановлен'); self.state.grid(row=1,column=0,sticky='w',pady=8)
        columns=('time','method','path','status','ms'); self.log=ttk.Treeview(f,columns=columns,show='headings')
        for col,title,width in [('time','Время',90),('method','Метод',80),('path','Путь',300),('status','Статус',90),('ms','Время, мс',100)]: self.log.heading(col,text=title); self.log.column(col,width=width,anchor='w')
        self.log.grid(row=2,column=0,sticky='nsew')
        buttons=ttk.Frame(f); buttons.grid(row=3,column=0,sticky='w',pady=8)
        ttk.Button(buttons,text='Очистить лог',command=lambda: [self.log.delete(i) for i in self.log.get_children()]).pack(side='left')
        ttk.Label(f,text='Маршруты: GET /, GET /time, GET /headers, GET /status/418, POST /echo').grid(row=4,column=0,sticky='w')

    def start_server(self):
        try: port=int(self.port.get())
        except ValueError: messagebox.showerror('Ошибка','Порт должен быть числом от 1 до 65535'); return
        if not 1<=port<=65535: messagebox.showerror('Ошибка','Порт должен быть от 1 до 65535'); return
        self.server=HttpServer(port,self.log_queue); self.server.start()

    def stop_server(self):
        if self.server: self.server.stop(); self.server=None
        self.state.config(text='● Остановлен')

    def open_browser(self):
        import webbrowser
        try: port=int(self.port.get())
        except ValueError: port=8080
        webbrowser.open(f'http://127.0.0.1:{port}/')

    def _poll_queue(self):
        try:
            while True:
                kind,data=self.log_queue.get_nowait()
                if kind=='state': self.state.config(text='● '+data)
                elif kind=='log': self.log.insert('', 'end', values=data)
                elif kind=='response':
                    status,headers,body=data; self.progress.config(text=f'Готово — HTTP {status}')
                    self.response.insert('end',f'HTTP status: {status}\n\nЗаголовки:\n{headers}\n\nТело:\n{body}')
                elif kind=='error': self.progress.config(text='Ошибка'); self.response.insert('end',data)
        except queue.Empty: pass
        self.root.after(100,self._poll_queue)

    def close(self):
        if self.server: self.server.stop()
        self.root.destroy()


def main():
    root=tk.Tk(); App(root); root.mainloop()

if __name__ == '__main__': main()
