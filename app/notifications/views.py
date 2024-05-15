from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Notification
from ..extensions import db
from . import notifications_bp
from collections import OrderedDict

@notifications_bp.route('/notifications')
@login_required
def notifications():
    user_notifications = Notification.query.filter_by(
        Users_idUser=current_user.idUser
    ).order_by(Notification.Timestamp.desc()).all()

    for notification in user_notifications:
        if notification.isar_id:
            notification.status_url = url_for('main.robot_status', isar_id=notification.isar_id)
        else:
            notification.status_url = None

    unique_notifications = OrderedDict()
    for notification in user_notifications:
        unique_key = (notification.Message, notification.Timestamp)
        if unique_key not in unique_notifications:
            unique_notifications[unique_key] = notification

    filtered_notifications = list(unique_notifications.values())

    return render_template('notifications/notifications.html',
                           notifications=filtered_notifications)



@notifications_bp.route('/delete_notification/<int:notification_id>', methods=['POST'])
@login_required
def delete_notification(notification_id):
    notification = Notification.query.get(notification_id)
    if notification and notification.Users_idUser == current_user.idUser:
        Notification.query.filter(
            Notification.Message == notification.Message,
            Notification.Timestamp == notification.Timestamp,
            Notification.Users_idUser == current_user.idUser
        ).delete()
        db.session.commit()
        flash('Notifikasjon(er) slettet.', 'success')
    else:
        flash('Notifikasjon ikke funnet.', 'error')
    return redirect(url_for('notifications.notifications'))


@notifications_bp.route('/mark_all_read', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(Users_idUser=current_user.idUser).delete()
    db.session.commit()
    flash('Alle notifikasjoner er markert som lest.', 'success')
    return redirect(url_for('notifications.notifications'))
