#!/usr/bin/env python3
"""
Ark multimodal embedding proxy - converts Ark's multimodal embedding API to OpenAI format
Usage: Run as a local HTTP server, point memsearch to http://localhost:PORT
"""
import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error

ARK_API_KEY = "b15fd882-1da9-47cd-8242-17678df6034a"
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
ARK_ENDPOINT = "ep-20260224141518-mjpbs"

class ProxyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/v1/embeddings':
            self.send_error(404)
            return
        
        # Read request body
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        try:
            req_data = json.loads(body)
            # OpenAI format: {"model": "...", "input": "text" or ["text1", "text2"]}
            
            # Convert to list
            input_text = req_data.get('input', '')
            if isinstance(input_text, str):
                input_text = [input_text]
            
            # Call Ark API for each text (Ark multimodal doesn't support batch)
            embeddings = []
            for txt in input_text:
                ark_req = {
                    "model": ARK_ENDPOINT,
                    "input": [{"type": "text", "text": txt}]
                }
                
                ark_url = f"{ARK_BASE_URL}/embeddings/multimodal"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {ARK_API_KEY}"
                }
                
                req = urllib.request.Request(
                    ark_url,
                    data=json.dumps(ark_req).encode('utf-8'),
                    headers=headers,
                    method='POST'
                )
                
                with urllib.request.urlopen(req) as response:
                    ark_resp = json.loads(response.read())
                
                embeddings.append(ark_resp["data"]["embedding"])
            
            # Convert to OpenAI format
            openai_resp = {
                "object": "list",
                "data": [
                    {
                        "object": "embedding",
                        "embedding": emb,
                        "index": i
                    }
                    for i, emb in enumerate(embeddings)
                ],
                "model": req_data.get('model', ARK_ENDPOINT),
                "usage": {
                    "prompt_tokens": sum(len(t.split()) for t in input_text),
                    "total_tokens": sum(len(t.split()) for t in input_text)
                }
            }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(openai_resp).encode('utf-8'))
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_error(500, str(e))
    
    def log_message(self, format, *args):
        # Suppress logs
        pass

if __name__ == '__main__':
    port = 18765
    server = HTTPServer(('127.0.0.1', port), ProxyHandler)
    print(f"Ark embedding proxy running on http://127.0.0.1:{port}")
    print(f"Configure memsearch with:")
    print(f"  OPENAI_BASE_URL=http://127.0.0.1:{port}/v1")
    print(f"  OPENAI_API_KEY=dummy")
    server.serve_forever()
