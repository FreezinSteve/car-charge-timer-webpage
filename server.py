import json
import random
import time

from http.server import BaseHTTPRequestHandler
from routes.main import routes
from response.staticHandler import StaticHandler
from response.templateHandler import TemplateHandler
from response.badRequestHandler import BadRequestHandler
from response.sensorHandler import SensorHandler
from response.stringHandler import StringResponseHandler
from datetime import datetime
from urllib.parse import urlparse
from urllib.parse import parse_qs

import requests

_state = 0

class Server(BaseHTTPRequestHandler):

     
    def do_HEAD(self):
        return

    def do_POST(self):
        global _state

        if self.path == "/boost":
            handler = StringResponseHandler()
            if _state == 0:
                _state = 2
            elif _state == 1:
                # No change
                pass
            else:
                if datetime.now().hour > 22 or datetime.now().hour < 9:
                    _state = 1
                else:
                    _state = 0

            handler.set_response("OK")
            handler.setStatus(200)
        elif self.path == "/reboot":
            handler = StringResponseHandler()
            handler.set_response(str("Module rebooting"))
            handler.setStatus(200)
        else:
            handler = StringResponseHandler()
            handler.set_response("Unknown route")
            handler.setStatus(404)
        self.respond({
            'handler': handler
        })

    def do_GET(self):
        global _state
        if self.path == "/":
            handler = StaticHandler()
            handler.find("/index.html")
        elif self.path == "/status":
            handler = StringResponseHandler()
            status = {}
            status["dt"] = datetime.now().replace(microsecond=0).isoformat()
            status["st"] = str(_state)
            json_msg = json.dumps(status)
            handler.set_response(json_msg)
        elif self.path == "/reboot":
            handler = StringResponseHandler()
            handler.set_response("Module rebooting")
        else:
            # Static files in public folder
            handler = StaticHandler()
            handler.find(self.path)
        self.respond({
            'handler': handler
        })

    def handle_http(self, handler):
        status_code = handler.getStatus()
        # time.sleep(0.5)
        self.send_response(status_code)

        if status_code is 200:
            content = handler.getContents()
            self.send_header('Content-type', handler.getContentType())
        else:
            content = "404 Not Found"

        self.end_headers()

        if isinstance(content, bytes):
            return content
        else:
            return bytes(content, 'UTF-8')

    def respond(self, opts):
        response = self.handle_http(opts['handler'])
        self.wfile.write(response)
