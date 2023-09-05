from interpreterClass import CanMessageInterpreter
import paho.mqtt.client as mqtt
import psycopg2
import time

conn = psycopg2.connect(
    dbname="wesmo",
    user="postgres",
    password="5545",
    host="localhost" 
)
cur = conn.cursor()

interpreter = CanMessageInterpreter()
interpreter.load_interpretations_from_csv('translation.csv')
BMSmessages = {}
# Function to handle a received message
def handle_message(canid, interpreted_message):
    global BMSmessages
    # Store the message in the dictionary
    BMSmessages[canid] = interpreted_message
    # If we have received all four messages, do something
    if len(BMSmessages) == 4 and all(key in BMSmessages for key in ["6B2", "6B3", "6B4", "6B5"]):
 #       print("storing messages")
 #       print(BMSmessages)

        query = """
        INSERT INTO BMS (PackCurrent0_1A, PackInstantaneousVoltage0_1V, PackStateOfCharge, PackAmphours0_1Ahr, PackHealth1, HighTemperatureC, 
        HighTempCellID, LowTemperatureC, LowTempCellID, AverageTemperatureC, InternalTemperatureC, LowCellVoltage0_0001V, LowCellVoltageID, HighCellVoltage0_0001V, 
        HighCellVoltageID, AverageCellVoltage0_0001V) VALUES (
        %(PackCurrent0_1A)s, %(PackInstantaneousVoltage0_1V)s, %(PackStateOfCharge)s, %(PackAmphours0_1Ahr)s, %(PackHealth1)s, 
        %(HighTemperatureC)s, %(HighTempCellID)s, %(LowTemperatureC)s, %(LowTempCellID)s, %(AverageTemperatureC)s, %(InternalTemperatureC)s, 
        %(LowCellVoltage0_0001V)s, %(LowCellVoltageID)s, %(HighCellVoltage0_0001V)s, %(HighCellVoltageID)s, %(AverageCellVoltage0_0001V)s
        )
        """
        data = {
            'PackCurrent0_1A': float(BMSmessages.get('6B2', {}).get('PackCurrent0_1A', 0)),
            'PackInstantaneousVoltage0_1V': float(BMSmessages.get('06b2', {}).get('PackInstantaneousVoltage0_1V', 0)),
            'PackStateOfCharge': float(BMSmessages.get('6B2', {}).get('PackStateOfCharge', 0)),
            'PackAmphours0_1Ahr': float(BMSmessages.get('6B3', {}).get('PackAmphours0_1Ahr', 0)),
            'PackHealth1': float(BMSmessages.get('6B3', {}).get('PackHealth1', 0)),
            'HighTemperatureC': float(BMSmessages.get('6B3', {}).get('HighTemperatureC', 0)),
            'HighTempCellID': float(BMSmessages.get('6B3', {}).get('HighTempCellID', 0)),
            'LowTemperatureC': float(BMSmessages.get('6B3', {}).get('LowTemperatureC', 0)),
            'LowTempCellID': float(BMSmessages.get('6B3', {}).get('LowTempCellID', 0)),
            'AverageTemperatureC': float(BMSmessages.get('6B3', {}).get('AverageTemperatureC', 0)),
            'InternalTemperatureC': float(BMSmessages.get('6B4', {}).get('InternalTemperatureC', 0)),
            'LowCellVoltage0_0001V': float(BMSmessages.get('6B4', {}).get('LowCellVoltage0_0001V', 0)),
            'LowCellVoltageID': float(BMSmessages.get('6B4', {}).get('LowCellVoltageID', 0)),
            'HighCellVoltage0_0001V': float(BMSmessages.get('6B4', {}).get('HighCellVoltage0_0001V', 0)),
            'HighCellVoltageID': float(BMSmessages.get('6B4', {}).get('HighCellVoltageID', 0)),
            'AverageCellVoltage0_0001V': float(BMSmessages.get('6B5', {}).get('AverageCellVoltage0_0001V', 0)),
        }
        cur.execute(query, data)
        conn.commit()

        BMSmessages = {}


############################ MQTT Methods #################################
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("newTopic")

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    result = interpreter.interpret(message)
#    print("something")
    if result is not None:
        canid, interpreted_message = result
        if canid in ["6B2", "6B3", "6B4", "6B5"]:
#            print("handling interpreted message")
            handle_message(canid, interpreted_message)

        # print(type(canid))
        # print(canid)
        # if rpm request to motor controller
        # if bytes(canid, 'utf-8').hex() == bytes(str(6000009), 'utf-8').hex():
        if canid == "06000009":
            query = "INSERT INTO data (speed) VALUES (%(speed)s)"
            data = {
                'speed': int(interpreted_message.get('ThrottleRequest0_10000')),
            }
            cur.execute(query, data)
            conn.commit()

        if canid == "06000008":
            query = "INSERT INTO state (vcuState) VALUES (%(vcuState)s)"
            data = {
                'vcuState': int(interpreted_message.get('VCUState')),
            }
            cur.execute(query, data)
            conn.commit()

        if canid == "06000007":
            ERROR_PEDAL_SENSORS_DISAGREE = 0x01     # Binary: 00000001
            ERROR_SAFETY_CIRCUIT_TRIPPED = 0x02     # Binary: 00000010
            ERROR_CAN_FAILED_TO_SEND = 0x04         # Binary: 00000100
            ERROR_LOOP_TIME_OVER_5MS = 0x08         # Binary: 00001000
            ERROR_IMD_ERROR = 0x10                  # Binary: 00010000
            
            errorCode = int(interpreted_message.get('ErrorCodes'))
            
            query = "INSERT INTO errorcodes (pedalsensor,safetycircuit,canfailed,looptoolong,errorimd) VALUES (%(pedalsensor)s, %(safetycircuit)s, %(canfailed)s, %(looptoolong)s, %(errorimd)s)"
            data = {
                'pedalsensor': 1 if errorCode & ERROR_PEDAL_SENSORS_DISAGREE else 0,
                'safetycircuit': 1 if errorCode & ERROR_SAFETY_CIRCUIT_TRIPPED else 0,
                'canfailed': 1 if errorCode & ERROR_CAN_FAILED_TO_SEND else 0,
                'looptoolong': 1 if errorCode & ERROR_LOOP_TIME_OVER_5MS else 0,
                'errorimd': 1 if errorCode & ERROR_IMD_ERROR else 0,
            }
            cur.execute(query, data)
            conn.commit()

        output = f"CANID: {canid}, " + ', '.join([f"{name}: {value}" for name, value in interpreted_message.items()])
        print(output)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("13.55.132.107", 1883, 60)

client.loop_forever()

