from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

users = {}  # Store username and their socket ID

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('register')
def handle_register(username):
    """
    Register a new user and validate the username.
    """
    if not username or username.strip() == "":
        emit('registration_error', {'error': 'Username cannot be empty!'}, to=request.sid)
        return
    
    if username in users:
        emit('registration_error', {'error': 'Username already exists!'}, to=request.sid)
        return

    # Add user to the users list
    users[username] = request.sid
    emit('update_users', list(users.keys()), broadcast=True)

@socketio.on('send_message')
def handle_send_message(data):
    """
    Send a private message to a specific user.
    """
    recipient = data['recipient']
    message = data['message']
    sender = data['sender']

    recipient_sid = users.get(recipient)
    if recipient_sid:
        emit('receive_message', {'sender': sender, 'message': message}, to=recipient_sid)

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle user disconnection and update the user list.
    """
    disconnected_user = None
    for username, sid in users.items():
        if sid == request.sid:
            disconnected_user = username
            break
    if disconnected_user:
        del users[disconnected_user]
        emit('update_users', list(users.keys()), broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
