from flask import render_template, request, jsonify, make_response
from . import history_bp
import os
import json
from datetime import datetime
from math import ceil
from ..models import Result
from ..extensions import db
from collections import OrderedDict
from flask_login import login_required

@history_bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    robot_name = request.args.get('robot_name', '')
    sort_order = request.args.get('sort', 'desc')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    query = request.args.get('query', '')
    status_filter = request.args.get('status_filter', 'all')
    per_page = 10

    inspection_data = get_inspection_data(
        page=page,
        per_page=per_page,
        robot_name=robot_name,
        sort_order=sort_order,
        from_date=from_date,
        to_date=to_date,
        query=query,
        status_filter=status_filter
    )

    total_results = get_filtered_results_count(
        robot_name=robot_name,
        from_date=from_date,
        to_date=to_date,
        query=query,
        status_filter=status_filter
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
        to_date=to_date,
        status_filter=status_filter
    )


def format_timestamp(timestamp):
    dt = parse_timestamp(timestamp)
    formatted_date = dt.strftime('%Y-%m-%d')
    formatted_time = dt.strftime('%H:%M:%S')
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

def parse_timestamp(timestamp):
    formats = ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"]
    for fmt in formats:
        try:
            return datetime.strptime(timestamp, fmt)
        except ValueError:
            continue
    raise ValueError(f"time data '{timestamp}' does not match any known format")


def get_inspection_data(page=1, per_page=10, sort_order='desc', robot_name='', from_date='', to_date='', query='', status_filter='all', results_dir='/home/dennis/isar/results'):
    inspection_data = []
    
    if status_filter in ['all', 'completed']:
        json_files = list(list_json_files(results_dir))
        for json_file in json_files:
            data = read_json_file(json_file)
            for item in data.get('data', []):
                for file_info in item.get('files', []):
                    if robot_name and data['additional_meta']['robot_name'] != robot_name:
                        continue
                    if query and query.lower() not in data['additional_meta']['mission_name'].lower():
                        continue
                    timestamp = file_info.get('timestamp')
                    if timestamp:
                        date_obj = parse_timestamp(timestamp).date()
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
                            'timestamp': timestamp,
                            'status': 'completed',
                            'details': ''
                        })
    
    if status_filter in ['all', 'failed']:
        results = Result.query
        if robot_name:
            results = results.filter_by(RobotName=robot_name)
        if from_date:
            results = results.filter(Result.Timestamp >= from_date)
        if to_date:
            results = results.filter(Result.Timestamp <= to_date)
        if query:
            results = results.filter(Result.MissionName.contains(query))
        if status_filter == 'failed':
            results = results.filter_by(Status='failed')

        if sort_order == 'asc':
            results = results.order_by(Result.Timestamp.asc())
        else:
            results = results.order_by(Result.Timestamp.desc())

        results = results.paginate(page=page, per_page=per_page, error_out=False).items

        for result in results:
            inspection_data.append({
                'mission_name': result.MissionName,
                'robot_name': result.RobotName,
                'date': result.Timestamp.strftime('%Y-%m-%d'),
                'time': result.Timestamp.strftime('%H:%M:%S'),
                'result_id': result.idResult,
                'timestamp': result.Timestamp.isoformat(),
                'status': result.Status,
                'details': result.Details
            })
    
    unique_inspection_data = OrderedDict()
    for item in inspection_data:
        unique_key = (item['mission_name'], item['robot_name'], item['date'], item['time'], item['status'], item.get('details', ''))
        if unique_key not in unique_inspection_data:
            unique_inspection_data[unique_key] = item

    sorted_inspection_data = list(unique_inspection_data.values())
    sorted_inspection_data.sort(key=lambda x: parse_timestamp(x['timestamp']), reverse=(sort_order == 'desc'))

    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    return sorted_inspection_data[start_index:end_index]

def get_filtered_results_count(robot_name='', from_date='', to_date='', query='', status_filter='all', results_dir='/home/dennis/isar/results'):
    count = 0
    if status_filter in ['all', 'completed']:
        for json_file in list_json_files(results_dir):
            data = read_json_file(json_file)
            if robot_name and data['additional_meta']['robot_name'] != robot_name:
                continue
            if query and query.lower() not in data['additional_meta']['mission_name'].lower():
                continue
            timestamp = data.get('data', [{}])[0].get('files', [{}])[0].get('timestamp', '')
            if timestamp:
                date_obj = parse_timestamp(timestamp).date()
                if from_date and date_obj < datetime.strptime(from_date, '%Y-%m-%d').date():
                    continue
                if to_date and date_obj > datetime.strptime(to_date, '%Y-%m-%d').date():
                    continue
                count += 1

    if status_filter in ['all', 'failed']:
        results_count = Result.query
        if robot_name:
            results_count = results_count.filter_by(RobotName=robot_name)
        if from_date:
            results_count = results_count.filter(Result.Timestamp >= from_date)
        if to_date:
            results_count = results_count.filter(Result.Timestamp <= to_date)
        if query:
            results_count = results_count.filter(Result.MissionName.contains(query))
        if status_filter == 'failed':
            results_count = results_count.filter_by(Status='failed')

        count += results_count.count()
    return count


@history_bp.route('/search-history')
@login_required
def search_history():
    query = request.args.get('query', '')
    robot_name = request.args.get('robot_name', '')
    sort_order = request.args.get('sort', 'desc')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')

    filtered_data = get_inspection_data(
        query=query,
        robot_name=robot_name,
        sort_order=sort_order,
        from_date=from_date,
        to_date=to_date
    )
    return jsonify(filtered_data)

@history_bp.route('/delete-report', methods=['DELETE'])
def delete_report():
    result_id = request.args.get('result_id')
    status = request.args.get('status')
    
    if not result_id or not status:
        response = make_response(jsonify({"error": "Result ID and status are required"}), 400)
        return response

    if status == 'completed':
        results_dir = '/home/dennis/isar/results'
        json_files = list(list_json_files(results_dir))
        for json_file in json_files:
            data = read_json_file(json_file)
            for item in data.get('data', []):
                for file_info in item.get('files', []):
                    if extract_result_id(file_info['file_name']) == result_id:
                        try:
                            os.remove(json_file)
                            response = make_response(jsonify({"success": "Report deleted successfully"}), 200)
                            return response
                        except Exception as e:
                            response = make_response(jsonify({"error": str(e)}), 500)
                            return response

    elif status == 'failed':
        results = Result.query.filter_by(idResult=result_id).all()
        if not results:
            response = make_response(jsonify({"error": "Result not found"}), 404)
            return response

        try:
            for result in results:
                db.session.delete(result)
            db.session.commit()
            response = make_response(jsonify({"success": "Report deleted successfully"}), 200)
            return response
        except Exception as e:
            response = make_response(jsonify({"error": str(e)}), 500)
            return response

    response = make_response(jsonify({"error": "Invalid status"}), 400)
    return response