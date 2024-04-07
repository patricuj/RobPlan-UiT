from flask import render_template, request
from . import history_bp
import os
import json
from datetime import date, datetime
from math import ceil


@history_bp.route('/history')
def history():
    page = request.args.get('page', 1, type=int)
    robot_name = request.args.get('robot_name', '')
    sort_order = request.args.get('sort', 'desc')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    per_page = 10

    inspection_data = get_inspection_data(
        page=page, 
        per_page=per_page, 
        robot_name=robot_name, 
        sort_order=sort_order, 
        from_date=from_date, 
        to_date=to_date
    )
    
    total_results = get_filtered_results_count(
        robot_name=robot_name, 
        from_date=from_date, 
        to_date=to_date
    )
    
    max_page = ceil(total_results / per_page)

    return render_template(
        'history/history.html', 
        inspection_data=inspection_data, 
        page=page, 
        max_page=max_page, 
        sort_order=sort_order, 
        selected_robot=robot_name,
        from_date=from_date, 
        to_date=to_date
    )


def format_timestamp(timestamp):
    dt = datetime.fromisoformat(timestamp)
    formatted_date = dt.strftime('%Y-%m-%d')
    formatted_time = dt.strftime('%H:%M')
    return formatted_date, formatted_time

def read_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def extract_result_id(file_name):
    parts = file_name.split('__Image__')
    if len(parts) > 1:
        number_part = parts[1].split('.')[0]
        return number_part
    return "Ukjent"


def list_json_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                yield os.path.join(root, file)

def get_inspection_data(page=1, per_page=10, sort_order='desc', robot_name='', from_date='', to_date='', results_dir='/home/dennis/isar/results'):
    inspection_data = []
    json_files = list(list_json_files(results_dir))

    for json_file in json_files:
        data = read_json_file(json_file)
        for item in data.get('data', []):
            for file_info in item.get('files', []):
                if robot_name and data['additional_meta']['robot_name'] != robot_name:
                    continue
                timestamp = file_info.get('timestamp')
                if timestamp:
                    date_obj = datetime.strptime(timestamp.split('T')[0], '%Y-%m-%d').date()
                    if from_date and date_obj < datetime.strptime(from_date, '%Y-%m-%d').date():
                        continue
                    if to_date and date_obj > datetime.strptime(to_date, '%Y-%m-%d').date():
                        continue
                    date, time = format_timestamp(timestamp)
                    inspection_data.append({
                        'mission_name': data['additional_meta']['mission_name'],
                        'robot_name': data['additional_meta']['robot_name'],
                        'date': date,
                        'time': time,
                        'result_id': extract_result_id(file_info['file_name']),
                        'timestamp': timestamp
                    })

    if sort_order == 'asc':
        inspection_data.sort(key=lambda x: datetime.strptime(x['timestamp'], "%Y-%m-%dT%H:%M:%S.%f"))
    else:
        inspection_data.sort(key=lambda x: datetime.strptime(x['timestamp'], "%Y-%m-%dT%H:%M:%S.%f"), reverse=True)

    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    return inspection_data[start_index:end_index]

def get_filtered_results_count(robot_name='', from_date='', to_date='', results_dir='/home/dennis/isar/results'):
    count = 0
    for json_file in list_json_files(results_dir):
        data = read_json_file(json_file)
        if robot_name and data['additional_meta']['robot_name'] != robot_name:
            continue
        timestamp = data.get('data', [{}])[0].get('files', [{}])[0].get('timestamp', '')
        if timestamp:
            date_obj = datetime.strptime(timestamp.split('T')[0], '%Y-%m-%d').date()
            if from_date and date_obj < datetime.strptime(from_date, '%Y-%m-%d').date():
                continue
            if to_date and date_obj > datetime.strptime(to_date, '%Y-%m-%d').date():
                continue
            count += 1
    return count

