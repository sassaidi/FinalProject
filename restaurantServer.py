from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import psycopg2
from psycopg2 import Error

# Database connection parameters
db_name = "restaurant"
db_user = "postgres"
db_password = "root"
db_host = "localhost"
db_port = "5432"

class RestaurantDatabase:
    def __init__(self):
        # Initialize database connection
        try:
            self.connection = psycopg2.connect(
                database=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            print("Connected to database successfully")
        except (Exception, Error) as error:
            print("Error connecting to PostgreSQL:", error)

    def __del__(self):
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            print("PostgreSQL connection is closed")

    def addReservation(self, customer_id, reservation_time, number_of_guests, special_requests):
        try:
            cursor = self.connection.cursor()
            insert_query = '''
                INSERT INTO reservations (customerId, reservationTime, numberOfGuests, specialRequests)
                VALUES (%s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (customer_id, reservation_time, number_of_guests, special_requests))
            self.connection.commit()
            print("Reservation added successfully")
        except Error as e:
            print("Error adding reservation:", e)

    def getAllReservations(self):
        try:
            cursor = self.connection.cursor()
            select_query = "SELECT * FROM reservations"
            cursor.execute(select_query)
            records = cursor.fetchall()
            return records
        except Error as e:
            print("Error fetching reservations:", e)
            return []

class RestaurantPortalHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.database = RestaurantDatabase()
        super().__init__(*args, **kwargs)
        
    def do_POST(self):
        try:
            if self.path == '/addReservation':
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                customer_id = int(form.getvalue("customer_id"))
                reservation_time = form.getvalue("reservation_time")
                number_of_guests = int(form.getvalue("number_of_guests"))
                special_requests = form.getvalue("special_requests")

                self.database.addReservation(customer_id, reservation_time, number_of_guests, special_requests)

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><head><title>Restaurant Portal</title></head>")
                self.wfile.write(b"<body>")
                self.wfile.write(b"<center><h1>Reservation Added</h1>")
                self.wfile.write(b"<hr>")
                self.wfile.write(b"<div><a href='/addReservation'>Add Another Reservation</a></div>")
                self.wfile.write(b"<div><a href='/'>Home</a></div>")
                self.wfile.write(b"</center></body></html>")

        except Exception as e:
            self.send_error(500, f'Internal Server Error: {e}')
    
    def do_GET(self):
        try:
            if self.path == '/':
                self.handle_root_request()
            elif self.path == '/addReservation':
                self.render_add_reservation_form()
            elif self.path == '/viewReservations':
                self.view_all_reservations()
            else:
                self.send_error(404, f'File Not Found: {self.path}')

        except Exception as e:
            self.send_error(500, f'Internal Server Error: {e}')

    def handle_root_request(self):
        try:
            # Fetch all reservations from the database
            records = self.database.getAllReservations()

            # Start building the HTML response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Begin HTML content
            self.wfile.write(b"<html><head><title>Restaurant Portal</title></head>")
            self.wfile.write(b"<body>")
            self.wfile.write(b"<center><h1>Restaurant Portal</h1>")
            self.wfile.write(b"<hr>")
            self.wfile.write(b"<div> <a href='/'>Home</a>| \
                             <a href='/addReservation'>Add Reservation</a>|\
                             <a href='/viewReservations'>View Reservations</a></div>")
            self.wfile.write(b"<hr><h2>All Reservations</h2>")
            self.wfile.write(b"<table border=1>")
            self.wfile.write(b"<tr><th>Reservation ID</th><th>Customer ID</th><th>Reservation Time</th><th>Number of Guests</th><th>Special Requests</th></tr>")

            # Iterate through records and build table rows
            for row in records:
                self.wfile.write(b"<tr>")
                for item in row:
                    self.wfile.write(f"<td>{item}</td>".encode())
                self.wfile.write(b"</tr>")

            # End HTML content
            self.wfile.write(b"</table></center>")
            self.wfile.write(b"</body></html>")
        
        except Error as e:
            self.send_error(500, f'Internal Server Error: {e}')

    def render_add_reservation_form(self):
        # This method remains the same as before
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><head><title>Add Reservation</title></head>")
        self.wfile.write(b"<body>")
        self.wfile.write(b"<center><h1>Add Reservation</h1>")
        self.wfile.write(b"<form method='post' action='/addReservation'>")
        self.wfile.write(b"Customer ID: <input type='text' name='customer_id'><br>")
        self.wfile.write(b"Reservation Time: <input type='text' name='reservation_time'><br>")
        self.wfile.write(b"Number of Guests: <input type='text' name='number_of_guests'><br>")
        self.wfile.write(b"Special Requests: <input type='text' name='special_requests'><br>")
        self.wfile.write(b"<input type='submit' value='Add Reservation'>")
        self.wfile.write(b"</form>")
        self.wfile.write(b"</center></body></html>")

    def view_all_reservations(self):
        # This method remains the same as before
        records = self.database.getAllReservations()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><head><title>Restaurant Portal</title></head>")
        self.wfile.write(b"<body>")
        self.wfile.write(b"<center><h1>Restaurant Portal</h1>")
        self.wfile.write(b"<hr>")
        self.wfile.write(b"<div> <a href='/'>Home</a>| \
                         <a href='/addReservation'>Add Reservation</a>|\
                         <a href='/viewReservations'>View Reservations</a></div>")
        self.wfile.write(b"<hr><h2>All Reservations</h2>")
        self.wfile.write(b"<table border=1>")
        self.wfile.write(b"<tr><th>Reservation ID</th><th>Customer ID</th><th>Reservation Time</th><th>Number of Guests</th><th>Special Requests</th></tr>")
        for row in records:
            self.wfile.write(b"<tr>")
            for item in row:
                self.wfile.write(f"<td>{item}</td>".encode())
            self.wfile.write(b"</tr>")
        self.wfile.write(b"</table></center>")
        self.wfile.write(b"</body></html>")

def run(server_class=HTTPServer, handler_class=RestaurantPortalHandler, port=8000):
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
