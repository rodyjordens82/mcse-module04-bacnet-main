import time
import BAC0
import mysql.connector
import os

# Connect to the MySQL database
conn = mysql.connector.connect(
    host="172.20.0.100",
    user="beheer",
    password="Geheim123!",
    database="db"
)
cursor = conn.cursor()

bacnet = BAC0.lite(ip='172.20.0.101/24', port='47809')

def read_database_write_controller():
    cursor.execute("SELECT status FROM light WHERE id = 1")
    light = cursor.fetchone()[0]

    cursor.execute("SELECT status FROM locking WHERE id = 1")
    locking = cursor.fetchone()[0]

    cursor.execute("SELECT status FROM fire WHERE id = 1")
    fire = cursor.fetchone()[0]

    cursor.execute("SELECT status FROM camera WHERE id = 1")
    camera = cursor.fetchone()[0]

    command1 = '172.20.0.102 analogValue 1 presentValue ' + str(light)
    command2 = '172.20.0.102 analogValue 2 presentValue ' + str(locking)
    command3 = '172.20.0.102 analogValue 3 presentValue ' + str(fire)
    command4 = '172.20.0.102 analogValue 4 presentValue ' + str(camera)

    print(command1)
    bacnet.write(command1)
    print(command2)
    bacnet.write(command2)
    print(command3)
    bacnet.write(command3)
    print(command4)
    bacnet.write(command4)

def read_controller_write_database():
    light = bacnet.read('172.20.0.102 analogValue 1 presentValue')
    locking = bacnet.read('172.20.0.102 analogValue 2 presentValue')
    fire = bacnet.read('172.20.0.102 analogValue 3 presentValue')
    camera = bacnet.read('172.20.0.102 analogValue 4 presentValue')

    # Update the MySQL database
    cursor.execute("UPDATE light SET status = %s WHERE id = 1", (light,))
    cursor.execute("UPDATE locking SET status = %s WHERE id = 1", (locking,))
    cursor.execute("UPDATE fire SET status = %s WHERE id = 1", (fire,))
    cursor.execute("UPDATE camera SET status = %s WHERE id = 1", (camera,))
    conn.commit()

def main():
    while True:
        print("process_id:", os.getpid())
        read_database_write_controller()
        time.sleep(0.1)
        read_controller_write_database()
        time.sleep(0.1)

if __name__ == '__main__':
    main()
