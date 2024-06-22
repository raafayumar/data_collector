import csv
import time
from struct import unpack_from
import json
import numpy as np
from websocket import create_connection

DTYPES = {
    0: np.int8,
    1: np.uint8,
    2: np.int16,
    3: np.uint16,
    4: np.int32,
    5: np.uint32,
    6: np.float32,
    7: np.float64,
}
ASCII_RS = '\u001e'
ASCII_US = '\u001f'

listener = None
frame_id = 0


def to_message(buffer):
    """ parse MatNet messages from JSON / Vayyar internal binary format """
    if isinstance(buffer, str):
        return json.loads(buffer)
    seek = 0
    fields_len = unpack_from('i', buffer, seek + 4)[0]
    fields_split = unpack_from(str(fields_len) + 's', buffer, seek +8)[0].decode('utf8').split(ASCII_RS)
    msg = {'ID': fields_split[0], 'Payload':dict.fromkeys(fields_split[1].split(ASCII_US))}
    seek += 8 + fields_len
    for key in msg['Payload']:
        seek += np.int32().nbytes
        dtype = DTYPES[(np.frombuffer(buffer, np.int32, 1, seek)).item()]
        seek += np.int32().nbytes
        ndims = (np.frombuffer(buffer, np.int32, 1, seek)).item()
        seek += np.int32().nbytes
        dims = np.frombuffer(buffer, np.int32, ndims, seek)
        seek += ndims * np.int32().nbytes
        data = np.frombuffer(buffer, dtype, np.prod(dims), seek)
        seek += np.prod(dims) * dtype().nbytes
        msg['Payload'][key] = data.reshape(dims) if ndims else data.item()
    return msg


def config_vayyar():
    global listener

    listener = create_connection("ws://127.0.0.1:1234/")

    listener.send(json.dumps({
        'Type': 'COMMAND',
        'ID': 'SET_PARAMS',
        'Payload': {
            'FlowCfg.save_dir': r'',
            'FlowCfg.read_from_file': 0.0,
            'FlowCfg.save_to_file': 0.0,
            'ExternalData.VAYYAR_IGNITION': 0,
            'ExternalData.VAYYAR_ENGINE': 0,
            'ExternalData.VAYYAR_SB1': 0,
            'ExternalData.VAYYAR_DOOR1': 0
        }
    }))

    # set outputs for each frame
    listener.send(json.dumps({
        'Type': 'COMMAND',
        'ID': 'START',
        'Payload': {
            'binary_outputs': [
                'Vayyar_InCarRawPointCloud',
                'Vayyar_InCarProcessedPointCloud',
                'Vayyar_InCarSbrTargets_sbrIndication',
                'Vayyar_InCarSbrTargets_sbrClassification',
                'Vayyar_InCarTargetsCpd',
                'Vayyar_InCarPresence',
                'Vayyar_InCarCpdIndication',
                'Vayyar_InCarMonitoredSeats',
                'Vayyar_InCarOccupancy',
                'Vayyar_InCarLsInSeat',
                'Vayyar_InCarLsInFootwell',
                'Vayyar_InCarCpdTargets_cpdClassification'
            ]
        }
    }))

    listener.send(json.dumps({'Type': 'QUERY', 'ID': 'BINARY_DATA'}))

    print("Running! Waiting for messages...")


def get_vayyar_data(path):
    global frame_id
    buffer = listener.recv()
    data = to_message(buffer)

    if data['ID'] == 'BINARY_DATA':
        save_to_csv(data['Payload'], path)  # Save data to CSV with unique frame ID
        frame_id += 1
        listener.send(json.dumps({'Type': 'QUERY', 'ID': 'BINARY_DATA'}))

    if data['ID'] == 'GET_STATUS':
        print(data['Payload']['status'])


def save_to_csv(data, file_path):
    """ Save the specified variables to a CSV file """
    fieldnames = ['rawX', 'rawY', 'rawZ', 'rawAMP',
                  'processedX', 'processedY', 'processedZ', 'processedAMP',
                  'Vayyar_InCarSbrTargets_sbrIndication',
                  'Vayyar_InCarSbrTargets_sbrClassification',
                  'Vayyar_InCarTargetsCpd',
                  'Vayyar_InCarPresence',
                  'Vayyar_InCarCpdIndication',
                  'Vayyar_InCarMonitoredSeats',
                  'Vayyar_InCarOccupancy',
                  'Vayyar_InCarLsInSeat',
                  'Vayyar_InCarLsInFootwell',
                  'Vayyar_InCarCpdTargets_cpdClassification']

    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        raw_point_cloud = data.get('Vayyar_InCarRawPointCloud', [])
        processed_point_cloud = data.get('Vayyar_InCarProcessedPointCloud', [])

        # Prepare the rows to be written
        max_len = max(len(raw_point_cloud), len(processed_point_cloud), 1)
        for i in range(max_len):
            row = {}
            if i < len(raw_point_cloud):
                row.update({
                    'rawX': raw_point_cloud[i, 0],
                    'rawY': raw_point_cloud[i, 1],
                    'rawZ': raw_point_cloud[i, 2],
                    'rawAMP': raw_point_cloud[i, 3]
                })
            if i < len(processed_point_cloud):
                row.update({
                    'processedX': processed_point_cloud[i, 0],
                    'processedY': processed_point_cloud[i, 1],
                    'processedZ': processed_point_cloud[i, 2],
                    'processedAMP': processed_point_cloud[i, 3]
                })
            if i == 0:  # Only include other variables once per frame
                for key in fieldnames[8:]:
                    row[key] = data.get(key, None)
            writer.writerow(row)
