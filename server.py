import http.server
import os
import json


ALLOWED_IPS = ["127.0.0.1", "192.168.1.100", "54.39.29.75", "54.86.50.139"]

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def check_ip(self):
        return True
        # Check if the request is from an allowed IP address
        if self.client_address[0] not in ALLOWED_IPS:
            self.send_response(403)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Forbidden")
            return False
        return True

    def log_request(self, code='-', size='-'):
        if code == 200:
            # Only log successful requests
            super().log_request(code, size)

    def send_method_not_allowed(self):
        # Send a 405 Method Not Allowed response
        self.send_response(405)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Method Not Allowed")
        return

    def do_POST(self):
        if not self.check_ip():
            return

        # Read the request body
        length = int(self.headers["Content-Length"])
        body = self.rfile.read(length)

        fields = body.decode().split("|")
        plot_id = fields[0]

        # Use the plot-id field as the filename
        filename = f"plots/{plot_id}.txt"

        # Save the request body to a file
        try:
            with open(filename, "wb") as f:
                f.write(body)
        except Exception as e:
            print(e)

        # Send a response
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(f"Request received and saved to {filename}.txt".encode())

    def do_GET(self):
        if "/data-" in self.path:
            # Read the data
            try:
                files = os.listdir("plots")
            except Exception as e:
                print(e)
                self.send_response(500)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Internal Server Error")
                return
            path = self.path
            path = path.replace("/data-", "")
            path = path + ".txt"
            if path in files:
                filename = self.path
                filename = filename.replace("/data-", "")

                # Read the file
                try:
                    with open(f"plots/{filename}.txt", "r") as f:
                        file_contents = f.read()
                except Exception as e:
                    print(e)
                    self.send_response(500)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"Internal Server Error")
                    return
                # Send the data as a JSON object
                id = file_contents.split("|")[0]
                cpu = file_contents.split("|")[1]
                tps = file_contents.split("|")[2]
                time = file_contents.split("|")[3]
                playercount = file_contents.split("|")[4]
                playerdata = file_contents.split("|")[5]
                perplayerdata = playerdata.split(",")
                playerinfo = []
                
                for i in perplayerdata:
                    playerinfo.append(i.split(";"))

                data = {"id": file_contents.split("|")[0], "cpu": file_contents.split("|")[1], "tps": file_contents.split("|")[2], "time": file_contents.split("|")[3], "playercount": file_contents.split("|")[4], "playerinfo": playerinfo}
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Invalid file".encode())
        elif self.path == "/":
            if not self.check_ip():
                return

            # Read the plots directory
            try:
                files = os.listdir("plots")
            except Exception as e:
                print(e)
                self.send_response(500)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Internal Server Error")
                return

            # Generate an HTML page with a list of the files in the plots directory
            html = "<head><link href=\"data:image/x-icon;base64,AAABAAEAEBAQAAEABAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAAAAAAAAAAAAEAAAAAAAAACIjBQAAAAAAPv/hwCwhwIA5Oh9ALC1JgDAxxQA/f/UAOLoMQD+/+sAlnMAAKarJADS2RgA+/+oAAAAAAAAAAAAERERERERERERERERERERERERERoREREREREROqERERERERUTGhERERERYVExoRERERwRsQEaERERQRgREBGhER0RHBEVERoRd9JIxmtQOqGRESQRFrERoRkX0UjBGxAREZd9JIxmsRERERERERERERERERERERERERERERERERH//wAA//8AAP5/AAD8PwAA+p8AAPVPAADtZwAA27MAALu5AAAAAAAAc50AAKRrAADABwAA//8AAP//AAD//wAA\" rel=\"icon\" type=\"image/x-icon\" /><title>DF-Status</title></head><html><body><ul>"
            for file in files:
                file = file.replace(".txt", "")
                html += f"<li><a href='/{file}'>{file}</a></li>"
            html += "</ul></body></html>"

            # Send the HTML page as the response body
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            try:
                files = os.listdir("plots")
            except Exception as e:
                print(e)
                self.send_response(500)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Internal Server Error")
                return
            path = self.path
            path = path.replace("/", "")
            path = path + ".txt"
            if path in files:
                filename = self.path.split("/")[-1]

                # Read the file
                try:
                    with open(f"plots/{filename}.txt", "r") as f:
                        file_contents = f.read()
                except Exception as e:
                    print(e)
                    self.send_response(500)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"Internal Server Error")
                    return
                id = file_contents.split("|")[0]
                cpu = file_contents.split("|")[1]
                tps = file_contents.split("|")[2]
                time = file_contents.split("|")[3]
                playercount = file_contents.split("|")[4]
                playerdata = file_contents.split("|")[5]
                perplayerdata = playerdata.split(",")
                playerinfo = []
                
                for i in perplayerdata:
                    playerinfo.append(i.split(";"))
                
                playerinfo = f'{playerinfo}'
                playerinfo = playerinfo.replace("'", '"')
                
                html = f'''
                <!DOCTYPE html>
                <html lang="en">
                	<head>
                		<meta charset="UTF-8">
                		<meta http-equiv="X-UA-Compatible" content="IE=edge">
                		<meta name="viewport" content="width=device-width, initial-scale=1.0">
                		<title>dghjvrfswjzhfgvd</title>
<link href="data:image/x-icon;base64,AAABAAEAEBAQAAEABAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAgAAAAAAAAAAAAAAAEAAAAAAAAACIjBQAAAAAAPv/hwCwhwIA5Oh9ALC1JgDAxxQA/f/UAOLoMQD+/+sAlnMAAKarJADS2RgA+/+oAAAAAAAAAAAAERERERERERERERERERERERERERoREREREREROqERERERERUTGhERERERYVExoRERERwRsQEaERERQRgREBGhER0RHBEVERoRd9JIxmtQOqGRESQRFrERoRkX0UjBGxAREZd9JIxmsRERERERERERERERERERERERERERERERERH//wAA//8AAP5/AAD8PwAA+p8AAPVPAADtZwAA27MAALu5AAAAAAAAc50AAKRrAADABwAA//8AAP//AAD//wAA" rel="icon" type="image/x-icon" />
                		<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Comfortaa">
                		<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Anybody">
                		<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Fjalla One">
                		<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Cabin">
                	</head>
                	<body>
                		<div class="iddiv">
                			<h1 class="id">{id}</h1>
                		</div>
                		<div class="info">
                			<div class="infoone">
                				<h1 class="hinfo cpu">CPU Usage: {cpu}%</h1>
                				<h1 class="hinfo tps">Server TPS: {tps}</h1>
                				<h1 class="hinfo time">Timestamp: {time}</h1>
                			</div>
                			<div class="infotwo">
                				<h1 class="hinfo playercount">Player count: {playercount}</h1>
                				<select class="dropdown">
                				</select>

                				<h1 class="hinfo pinfo x">X:</h1>
                				<h1 class="hinfo pinfo y">Y:</h1>
                				<h1 class="hinfo pinfo z">Z:</h1>
                				<h1 class="hinfo pinfo pitch">Pitch:</h1>
                				<h1 class="hinfo pinfo yaw">Yaw:</h1>
                			</div>
                		</div>

                		<script>let dropdown = document.querySelector('.dropdown');
var playerinfo = "";

updateData()

let cpu = document.querySelector('.cpu');
let tps = document.querySelector('.tps');
let time = document.querySelector('.time');

let index = 0;

function updateData() {{
    fetch("/data-{id}").then(response => {{
        return response.json();
    }}).then(data => {{
        // Update the page with the new data
        playerinfo = data.playerinfo;
        cpu.innerHTML = `CPU Usage: ${{data.cpu}}%`;
        tps.innerHTML = `Server TPS: ${{data.tps}}`;
        time.innerHTML = `Timestamp: ${{data.time}}`;
        let usernames = [];
        for(let i of playerinfo) {{
            usernames.push(i[0]);
        }}

        if(dropdown.selectedIndex == -1){{
            dropdown.selectedIndex = 0;
        }}

        if (dropdown.children.length != 0) {{
            index = dropdown.selectedIndex;
            dropdown.innerHTML = "";
        }}

        usernames.forEach((option) => {{
            const newOption = document.createElement('option');
            newOption.value = option;
            newOption.text = option;
            dropdown.appendChild(newOption);
        }});

        dropdown.selectedIndex = index;
    }});

    setTimeout(updateData, 2000);
}}

setTimeout(() =>{{

let x = document.querySelector(".x");
let y = document.querySelector(".y");
let z = document.querySelector(".z");
let pitch = document.querySelector(".pitch");
let yaw = document.querySelector(".yaw");

updateInformation();

function updateInformation() {{
    for(let i of playerinfo) {{
        if(dropdown.selectedIndex == -1){{
            dropdown.selectedIndex = 0;
        }}
        if(i[0] === dropdown.options[dropdown.selectedIndex].text) {{
            x.innerHTML = `X: ${{i[1]}}`;
            y.innerHTML = `Y: ${{i[2]}}`;
            z.innerHTML = `Z: ${{i[3]}}`;
            pitch.innerHTML = `Pitch: ${{i[4]}}`;
            yaw.innerHTML = `Yaw: ${{i[5]}}`;
        }}
    }}

    setTimeout(() => {{
        updateInformation();
    }}, 10);
}}}}, 500)</script>
                        <style>body, html {{
	margin: 0;
	height: 100%;
}}

body {{
	background-color: #223;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-direction: column;
	row-gap: 10%;
}}

.id {{
	color: lightsalmon;
	font-size: 3em;
	font-family: 'Comfortaa';
}}

.iddiv {{
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: flex-start;
	position: relative;
}}

.info {{
	height: 50%;
	width: 80%;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-direction: row;
	column-gap: 3%;
}}

.infoone, .infotwo {{
	width: 50%;
	height: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-direction: column;
	border: 2px solid #112;
	border-radius: 15px;
	row-gap: 15%;
}}

.infotwo {{
	row-gap: 5% !important;
}}

.hinfo {{
	color: #33de97;
	margin: 0;
	font-size: 4vh;
	font-family: 'Cabin';
}}
.playercount {{
	color: #44eb6b;
}}

.dropdown {{
	border: none;
	margin: none;
	width: 50%;
	height: 8%;
	text-align: center;
	background-color: #333;
	color: white;
	font-family: 'Comfortaa';
	font-size: 3.5vh;
	border-radius: 10px;
}}

.pinfo {{
	font-size: 3vh;
}}</style>
                	</body>
                </html>
                '''

                # Send the HTML page as the response body
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Invalid file".encode())



    def do_HEAD(self):
        # Send a 405 Method Not Allowed response
        self.send_method_not_allowed()

    def do_PUT(self):
        # Send a 405 Method Not Allowed response
        self.send_method_not_allowed()

    def do_DELETE(self):
        # Send a 405 Method Not Allowed response
        self.send_method_not_allowed()

    def do_CONNECT(self):
        # Send a 405 Method Not Allowed response
        self.send_method_not_allowed()

    def do_OPTIONS(self):
        # Send a 405 Method Not Allowed response
        self.send_method_not_allowed()

    def do_TRACE(self):
        # Send a 405 Method Not Allowed response
        self.send_method_not_allowed()

    def do_PATCH(self):
        # Send a 405 Method Not Allowed response
        self.send_method_not_allowed()

server = http.server.HTTPServer(("", 8001), RequestHandler)
server.serve_forever()
