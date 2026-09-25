import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from ai import VisualPingPongEnv


HOST = "0.0.0.0"
PORT = 8000
env = VisualPingPongEnv(render_mode="rgb_array")
env.reset()

HTML = """<!doctype html>
<html lang="en">
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ping Pong Environment</title>
  <style>
    body { margin: 0; background: #171a1f; color: white; font: 16px system-ui, sans-serif; text-align: center; }
    main { max-width: 1000px; margin: auto; padding: 16px; }
    canvas { width: 100%; height: auto; image-rendering: pixelated; background: #6f6f6f; touch-action: none; }
    button { min-width: 110px; min-height: 48px; margin: 12px 5px 0; border: 0; border-radius: 8px; font-size: 18px; }
    #up { background: #00a8ff; } #stay { background: #d7dce2; } #down { background: #ff5959; }
  </style>
</head>
<body>
  <main>
    <h2>Ping Pong Environment</h2>
    <canvas id="board" width="1000" height="500"></canvas>
    <div>
      <button id="up">Up</button>
      <button id="stay">Stay</button>
      <button id="down">Down</button>
    </div>
  </main>
<script>
const canvas = document.getElementById('board');
const ctx = canvas.getContext('2d');
let action = 0;
function draw(state) {
  const cell = 10;
  ctx.fillStyle = 'rgb(111,111,111)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = 'black';
  ctx.lineWidth = 1;
  for (let row = 0; row < 50; row++) {
    for (let col = 0; col < 100; col++) {
      ctx.strokeRect(col * cell, row * cell, cell, cell);
    }
  }
  ctx.fillStyle = 'red';
  ctx.fillRect(0, 0, cell, canvas.height);
  ctx.fillStyle = '#00ff00';
  ctx.fillRect(state.ballx * cell, state.bally * cell, cell, cell);
  for (let offset = -2; offset <= 2; offset++) {
    ctx.fillRect(0, (state.paddle + offset) * cell, cell, cell);
  }
}
async function tick() {
  const response = await fetch('/state?action=' + action);
  const state = await response.json();
  draw(state);
  action = 0;
}
for (const [id, value] of [['up', 1], ['stay', 0], ['down', 2]]) {
  document.getElementById(id).addEventListener('click', () => { action = value; tick(); });
}
tick();
setInterval(tick, 100);
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            body = HTML.encode()
            content_type = "text/html; charset=utf-8"
        elif parsed.path == "/state":
            query = parse_qs(parsed.query)
            action = int(query.get("action", [0])[0])
            observation, reward, terminated, _, _ = env.step(action)
            if terminated:
                env.reset()
            body = json.dumps({
                "paddle": int(observation[0]),
                "ballx": int(observation[1]),
                "bally": int(observation[2]),
                "reward": reward,
            }).encode()
            content_type = "application/json"
        else:
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    print(f"Open http://localhost:{PORT} in a browser")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
