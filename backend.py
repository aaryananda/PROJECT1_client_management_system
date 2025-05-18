from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)

# Configure PostgreSQL connection
app.config['PG_HOST'] = 'dpg-d0l19s3uibrs739uj17g-a'  # Or copy the exact host shown in Render
app.config['PG_USER'] = 'cms_db_tv9y_user'         # e.g., render_user
app.config['PG_PASSWORD'] = 'rk5Q6isz1VgX5aqi9wEXmfdcpf4C8ANY' # copy from Render
app.config['PG_DB'] = 'cms_db_tv9y'           # copy from Render


# Function to establish a database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=app.config['PG_HOST'],
        database=app.config['PG_DB'],
        user=app.config['PG_USER'],
        password=app.config['PG_PASSWORD']
    )
    return conn

# Route to render the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to display all clients
@app.route('/clients', methods=['GET'])
def get_clients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients")
    clients = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('clients_a.html', clients=clients)
# Route to add a new client
@app.route('/clients/add', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        clientid = request.form['client_id']
        client_manager = request.form['client_manager']
        contact_info = request.form['contact_info']

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO clients (client_id, name, client_manager, contact_info) VALUES (%s, %s, %s, %s)",
                (clientid, name, client_manager, contact_info)
            )
            conn.commit()
            return redirect('/clients')
        except Exception as e:
            conn.rollback() 
        finally:
            cur.close()
            conn.close()
    return render_template('add_client_a.html')

# Route to update an existing client
@app.route('/clients/update/<int:id>', methods=['GET', 'POST'])
def update_client(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        client_manager = request.form['client_manager']
        contact_info = request.form['contact_info']
        services_used = request.form['services_used']  # This is now treated as text

        try:
            cur.execute(
                "UPDATE clients SET name = %s, client_manager = %s, contact_info = %s WHERE client_id = %s",
                (name, client_manager, contact_info, id)
            )
           # cur.execute(
            #    "UPDATE client_service SET service_id = %s WHERE client_id = %s",
             #   (services_used, id)  # Treat services_used as a string
            #)
            conn.commit()
        except Exception as e:
            print("An error occurred during update:", str(e))
            return "An error occurred during update."

        cur.close()
        conn.close()
        return redirect('/clients')

    cur.execute("SELECT * FROM clients WHERE client_id = %s", (id,))
    clients = cur.fetchone()
    cur.close()
    conn.close()

    if clients is None:
        return "Client not found", 404

    return render_template('update_client_a.html', client=clients)


# Route to delete a client
@app.route('/clients/delete/<int:id>', methods=['GET', 'POST'])
def delete_client(id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        cur.execute("DELETE FROM clients WHERE client_id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/clients')

    cur.execute("SELECT COUNT(*) FROM clients WHERE client_id = %s", (id,))
    usecase_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    if usecase_count > 0:
        return render_template('confirm_delete_a.html', client_id=id, usecase_count=usecase_count)
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM clients WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/clients')

# Route to display all services
@app.route('/services', methods=['GET'])
def get_services():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM services")
    services = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('services_a.html', services=services)
# to add service
@app.route('/services/add', methods=['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        service_description = request.form['service_description']
        resources_required = request.form['resources_required']
        estimated_cost = float(request.form['estimated_cost'])
        developing_team = request.form['developing_team']
        

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO services (service_description, resources_required, estimated_cost, developing_team) VALUES (%s, %s, %s, %s)",
                (service_description, resources_required, estimated_cost, developing_team)
            )
            conn.commit()
        except Exception as e:
            print(f"Error occurred: {e}")  # Log the error
            return "An error occurred while adding the service.", 500
        finally:
            cur.close()
            conn.close()

        return redirect('/services')
    return render_template('add_service_a.html')

#to delete service

@app.route('/service/delete/<int:id>', methods=['GET', 'POST'])
def delete_service(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        # Delete the service from the database
        cur.execute("DELETE FROM services WHERE service_id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/services')

    # Check if the service exists
    cur.execute("SELECT COUNT(*) FROM services WHERE service_id = %s", (id,))
    service_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    
    # If the service exists, render the confirmation page
    if service_count > 0:
        return render_template('confirm_delete_service_a.html', service_id=id)
    else:
        return redirect('/services')  # Redirect if the service doesn't exist
    
#to update service
@app.route('/service/update/<int:id>', methods=['GET', 'POST'])
def update_service(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Fetch the current service details
    if request.method == 'POST':
        service_description = request.form['service_description']
        resources_required = request.form['resources_required']
        estimated_cost = request.form['estimated_cost']
        developing_team = request.form['developing_team']
        
        
        # Update the service in the database
        cur.execute("""
            UPDATE services
            SET service_description = %s,
                resources_required = %s,
                estimated_cost = %s,
                developing_team = %s
             WHERE service_id = %s;
        """, (service_description, resources_required, estimated_cost, developing_team, id))
        
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/services')
    
    # Fetch the existing service data to populate the form
    cur.execute("SELECT * FROM services WHERE service_id = %s", (id,))
    service = cur.fetchone()
    cur.close()
    conn.close()
    
    if service:
        return render_template('update_service_a.html', service=service)
    else:
        return redirect('/services')  # Redirect if the service is not found

@app.route('/usecases/<int:client_id>', methods=['GET'])
def get_usecases(client_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Fetch the client from the clients table
    cur.execute("SELECT * FROM clients WHERE client_id = %s", (client_id,))
    client = cur.fetchone()
    
    usecases = []
    if client:
        cur.execute("""
        SELECT service_id, client_id, start_date, status, custom_price 
        FROM client_service WHERE client_id = %s
        """, (client_id,))
        usecases = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('usecases_a.html', usecases=usecases, client=client)

# Route to add a new use case for a specific client
@app.route('/usecases/add/<int:client_id>', methods=['GET', 'POST'])
def add_usecase(client_id):
    if request.method == 'POST':
        service_id = request.form['service_id']
        start_date = request.form['start_date']
        status = request.form['status']
        custom_price = request.form['custom_price']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO client_service (service_id, client_id, start_date, status, custom_price) VALUES (%s, %s, %s, %s, %s)",
            (service_id, client_id, start_date, status, custom_price))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(f'/usecases/{client_id}')
    
    return render_template('add_usecase_a.html', client_id=client_id)
# Route to update a specific use case
@app.route('/usecases/update/<int:id>', methods=['GET', 'POST'])
def update_usecase(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Fetch current usecase details based on ID
    cur.execute("SELECT * FROM client_service WHERE service_id = %s", (id,))
    usecase = cur.fetchone()
    
    if usecase is None:
        return "Usecase not found", 404

    client_id = usecase[1]  # Assuming the second column is client_id

    if request.method == 'POST':
        # Retrieve form data
        service_id = request.form['service_id']
        client_id = request.form['client_id']
        start_date = request.form['start_date']
        status = request.form['status']
        custom_price = float(request.form['custom_price'])

        # Update the use case
        cur.execute(
            "UPDATE client_service SET start_date = %s, status = %s, custom_price = %s WHERE service_id = %s",
            (start_date, status, custom_price, id)
        )
        conn.commit()

        cur.close()
        conn.close()
        return redirect(f'/usecases/{client_id}')
    
    cur.close()
    conn.close()
    return render_template('update_usecase.html', usecase=usecase, client_id=client_id)



# Route to delete a use case
@app.route('/usecase/delete/<int:id>', methods=['GET'])
def delete_usecase(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT client_id FROM usecases WHERE client_id = %s", (id,))
    client_id = cur.fetchone()[0]
    cur.execute("DELETE FROM client_service WHERE service_id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(f'/usecases/{client_id}')



# Route to display all client managers
@app.route('/client_managers', methods=['GET'])
def get_client_managers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM client_managers")
    managers = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('client_manager_a.html', managers=managers)

#route to add new client manager
@app.route('/client_managers/add', methods=['GET', 'POST'])
def add_client_managers():
    if request.method == 'POST':
        name = request.form['name']
        id = request.form['id']
        contact_info = request.form['contact_info']
        department = request.form['department']
        assigned_projects = request.form['assigned_projects']


        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO client_managers(id, name,contact_info,department,assigned_projects) VALUES (%s, %s, %s, %s,%s)",
                (id, name, contact_info,department,assigned_projects)
            )
            conn.commit()
            return redirect('/client_managers')
        except Exception as e:
            conn.rollback() 
        finally:
            cur.close()
            conn.close()
    return render_template('add_client_manager_a.html')

# Route to update a client manager
@app.route('/client_manager/update/<int:id>', methods=['GET', 'POST'])
def update_client_manager(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        # Fetch form data
        name = request.form.get('client_manager_name')
        contact_info = request.form.get('contact_info')
        department = request.form.get('department')
        assigned_projects = request.form.get('projects_assigned')
        
        # Update client manager data
        try:
            cur.execute("""
                UPDATE client_managers 
                SET name = %s, contact_info = %s, department = %s, assigned_projects = %s 
                WHERE id = %s
            """, (name, contact_info, department, assigned_projects,id))
            
            conn.commit()
        except Exception as e:
            print("An error occurred during update:", str(e))
            conn.rollback()
            return "An error occurred during update."
        finally:
            cur.close()
            conn.close()
        
        return redirect('/client_managers')
    
    # Retrieve the current client manager data to display in the form
    cur.execute("SELECT * FROM client_managers WHERE id = %s", (id,))
    manager = cur.fetchone()
    cur.close()
    conn.close()
    
    if manager is None:
        return "Client Manager not found", 404
    
    return render_template('update_client_manager_a.html', manager=manager)


@app.route('/client_manager/delete/<int:id>', methods=['GET', 'POST'])
def delete_client_manager(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # Delete the client manager with the given id
        cur.execute("DELETE FROM client_managers WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/client_managers')

    # Fetch client manager details for confirmation display
    cur.execute("SELECT * FROM client_managers WHERE id = %s", (id,))
    manager = cur.fetchone()
    cur.close()
    conn.close()

    if manager is None:
        return "Client Manager not found", 404

    # Pass manager details to confirmation template
    return render_template('client_manager_delete_a.html', manager=manager)


# Route to display all invoice
@app.route('/invoice', methods=['GET'])
def get_invoice():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM invoice")
    invoice = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('invoice.html', invoice=invoice)
# to add invoice
@app.route('/invoice/add', methods=['GET', 'POST'])
def add_invoice():
    if request.method == 'POST':
        invoice_id=request.form['invoice_id']
        client_id = request.form['client_id']
        service_id = request.form['service_id']
        invoice_date = request.form['invoice_date']
        total_amount = float(request.form['total_amount'])
        
        

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO invoice (invoice_id,client_id,service_id,invoice_date,total_amount) VALUES (%s,%s, %s, %s, %s)",
                (invoice_id,client_id,service_id,invoice_date,total_amount)
            )
            conn.commit()
        except Exception as e:
            print(f"Error occurred: {e}")  # Log the error
            return "An error occurred while adding the invoice.", 500
        finally:
            cur.close()
            conn.close()

        return redirect('/invoice')
    return render_template('add_invoice_a.html')

#to delete service

@app.route('/invoice/delete/<int:id>', methods=['GET', 'POST'])
def delete_invoice(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        # Delete the service from the database
        cur.execute("DELETE FROM invoice WHERE invoice_id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/invoice')

    # Check if the service exists
    cur.execute("SELECT COUNT(*) FROM invoice WHERE invoice_id = %s", (id,))
    service_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    
    # If the service exists, render the confirmation page
    if service_count > 0:
        return render_template('confirm_delete_invoice_a.html', invoice_id=id)
    else:
        return redirect('/invoice')  # Redirect if the service doesn't exist
    
#to update invoice
@app.route('/invoice/update/<int:id>', methods=['GET', 'POST'])
def update_invoice(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Fetch the current service details
    if request.method == 'POST':
        
        client_id = request.form['client_id']
        service_id = request.form['service_id']
        invoice_date = request.form['invoice_date']
        total_amount = float(request.form['total_amount'])
        
        
        # Update the service in the database
        cur.execute("""
            UPDATE invoice
            SET 
                client_id = %s,
                service_id = %s,
                invoice_date = %s,
                total_amount = %s
             WHERE invoice_id = %s;
        """, (client_id,service_id,invoice_date,total_amount, id))
        
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/invoice')
    
    # Fetch the existing service data to populate the form
    cur.execute("SELECT * FROM invoice WHERE invoice_id = %s", (id,))
    invoice = cur.fetchone()
    cur.close()
    conn.close()
    
    if invoice :
        return render_template('update_invoice_a.html', invoice=invoice)
    else:
        return redirect('/invoice')  # Redirect if the service is not found





if __name__ == '__main__':
    app.run(debug=True)
