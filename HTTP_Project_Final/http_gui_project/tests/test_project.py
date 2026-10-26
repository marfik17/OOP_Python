"""Unit and integration tests for the student HTTP client/server project."""
import json
import queue
import socket
import threading
import time
import unittest

from src.main import (
    BasicRouter, HTTPMessage, HttpClient, HttpError, HttpServer, ParsedURL,
    URLParser,
)


class URLParserTests(unittest.TestCase):
    def test_http_default_port(self):
        self.assertEqual(URLParser.parse('http://example.com').port, 80)

    def test_https_default_port_and_tls(self):
        parsed = URLParser.parse('https://example.com/a')
        self.assertEqual(parsed.port, 443)
        self.assertTrue(parsed.tls)

    def test_custom_port_and_query(self):
        parsed = URLParser.parse('http://localhost:8088/a?x=1#part')
        self.assertEqual((parsed.host, parsed.port, parsed.target), ('localhost', 8088, '/a?x=1'))

    def test_root_path(self):
        self.assertEqual(URLParser.parse('http://localhost:8080').target, '/')

    def test_reject_empty(self):
        with self.assertRaises(HttpError): URLParser.parse('')

    def test_reject_missing_scheme(self):
        with self.assertRaises(HttpError): URLParser.parse('localhost:8080')

    def test_reject_unsupported_scheme(self):
        with self.assertRaises(HttpError): URLParser.parse('ftp://example.com')

    def test_reject_bad_port(self):
        with self.assertRaises(HttpError): URLParser.parse('http://localhost:99999')

    def test_reject_credentials(self):
        with self.assertRaises(HttpError): URLParser.parse('http://user:pass@example.com')


class HTTPMessageTests(unittest.TestCase):
    def test_serialize_request(self):
        raw = HTTPMessage.serialize_request('GET', '/', {'Host': 'localhost'})
        self.assertTrue(raw.startswith(b'GET / HTTP/1.1\r\n'))
        self.assertTrue(raw.endswith(b'\r\n\r\n'))

    def test_serialize_post_with_body(self):
        raw = HTTPMessage.serialize_request('POST', '/echo', {'Content-Length': '3'}, b'abc')
        self.assertTrue(raw.endswith(b'\r\n\r\nabc'))

    def test_reject_invalid_target(self):
        with self.assertRaises(HttpError): HTTPMessage.serialize_request('GET', 'bad path', {}, b'')

    def test_parse_response(self):
        raw = b'HTTP/1.1 201 Created\r\nContent-Length: 2\r\nX-Test: yes\r\n\r\nok'
        status, reason, headers, body = HTTPMessage.parse_response(raw)
        self.assertEqual((status, reason, headers['x-test'], body), (201, 'Created', 'yes', b'ok'))

    def test_parse_empty_body(self):
        status, _, _, body = HTTPMessage.parse_response(b'HTTP/1.1 204 No Content\r\nContent-Length: 0\r\n\r\n')
        self.assertEqual((status, body), (204, b''))

    def test_reject_missing_separator(self):
        with self.assertRaises(HttpError): HTTPMessage.parse_response(b'HTTP/1.1 200 OK')

    def test_reject_invalid_status(self):
        with self.assertRaises(HttpError): HTTPMessage.parse_response(b'HTTP/1.1 xyz Nope\r\n\r\nx')

    def test_reject_invalid_content_length(self):
        with self.assertRaises(HttpError): HTTPMessage.parse_response(b'HTTP/1.1 200 OK\r\nContent-Length: abc\r\n\r\nx')

    def test_decode_chunked(self):
        self.assertEqual(HTTPMessage.decode_chunked(b'3\r\nabc\r\n2\r\nde\r\n0\r\n\r\n'), b'abcde')

    def test_decode_chunked_extension(self):
        self.assertEqual(HTTPMessage.decode_chunked(b'2;ext=yes\r\nhi\r\n0\r\n\r\n'), b'hi')

    def test_reject_broken_chunked(self):
        with self.assertRaises(HttpError): HTTPMessage.decode_chunked(b'Z\r\nabc\r\n0\r\n\r\n')

    def test_serialize_response_content_length(self):
        raw = HTTPMessage.serialize_response(200, 'OK', {'Content-Type': 'text/plain'}, b'hello')
        self.assertIn(b'Content-Length: 5\r\n', raw)
        self.assertTrue(raw.endswith(b'\r\n\r\nhello'))


class RouterTests(unittest.TestCase):
    def setUp(self): self.router = BasicRouter()

    def test_root(self):
        status, _, _, body = self.router.handle('GET', '/', {}, b'')
        self.assertEqual(status, 200); self.assertIn(b'Hello', body)

    def test_echo(self):
        status, _, content_type, body = self.router.handle('POST', '/echo', {'content-type':'text/plain'}, b'abc')
        self.assertEqual(status, 200); self.assertEqual(body, b'abc'); self.assertEqual(content_type, 'text/plain')

    def test_time_json(self):
        status, _, _, body = self.router.handle('GET', '/time', {}, b'')
        self.assertEqual(status, 200); self.assertIn('time', json.loads(body))

    def test_headers_json(self):
        status, _, _, body = self.router.handle('GET', '/headers', {'host':'localhost'}, b'')
        self.assertEqual(status, 200); self.assertEqual(json.loads(body)['host'], 'localhost')

    def test_status_418(self): self.assertEqual(self.router.handle('GET', '/status/418', {}, b'')[0], 418)
    def test_not_found(self): self.assertEqual(self.router.handle('GET', '/missing', {}, b'')[0], 404)
    def test_bad_status(self): self.assertEqual(self.router.handle('GET', '/status/9999', {}, b'')[0], 400)


class ClientValidationTests(unittest.TestCase):
    def test_bad_url(self):
        with self.assertRaises(HttpError): HttpClient().request('not a url')

    def test_set_timeout(self):
        client = HttpClient(timeout=2)
        client.set_timeout(1.5)
        self.assertEqual(client.timeout, 1.5)

    def test_reject_nonpositive_timeout(self):
        with self.assertRaises(ValueError): HttpClient().set_timeout(0)


class IntegrationTests(unittest.TestCase):
    """Exercise the real socket server and the real HTTP client together."""
    @classmethod
    def setUpClass(cls):
        cls.port = cls._free_port()
        cls.events = queue.Queue()
        cls.server = HttpServer(cls.port, cls.events)
        cls.server.start()
        deadline = time.time() + 3
        while time.time() < deadline:
            try:
                with socket.create_connection(('127.0.0.1', cls.port), timeout=.1): break
            except OSError: time.sleep(.05)
        else: raise RuntimeError('Test HTTP server did not start')
        cls.client = HttpClient(timeout=2)

    @classmethod
    def tearDownClass(cls): cls.server.stop()

    @staticmethod
    def _free_port():
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0)); return sock.getsockname()[1]

    def get(self, path='/'):
        return self.client.request(f'http://127.0.0.1:{self.port}{path}')

    def test_get_root_real_server(self):
        status, _, body = self.get('/')
        self.assertEqual(status, 200); self.assertIn('Python HTTP server works', body)

    def test_get_time_real_server(self):
        status, _, body = self.get('/time')
        self.assertEqual(status, 200); self.assertIn('time', json.loads(body))

    def test_get_headers_real_server(self):
        status, headers, body = self.get('/headers')
        self.assertEqual(status, 200); self.assertIn('application/json', headers); self.assertIn('host', body)

    def test_get_custom_status_real_server(self):
        status, _, body = self.get('/status/418')
        self.assertEqual(status, 418); self.assertIn("I'm a teapot", body)

    def test_unknown_route_real_server(self):
        status, _, body = self.get('/no-such-route')
        self.assertEqual(status, 404); self.assertIn('404', body)

    def test_post_echo_real_server(self):
        status, _, body = self.client.request(f'http://127.0.0.1:{self.port}/echo', 'POST', body='hello integration')
        self.assertEqual(status, 200); self.assertEqual(body, 'hello integration')


if __name__ == '__main__': unittest.main(verbosity=2)
