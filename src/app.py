from flask import *
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import random

def load_json(filename, default_value):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_value

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'src/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

users = load_json('users.json', ["admin"])
posts = load_json('posts.json', [{"title": "Test", "author": "vskpsk", "content": "Tohle je testovaci post!"}])
images = load_json('images.json', ["00000000000000.jpg"])


@app.route('/')
def index():
    cookie_value = request.cookies.get('username')

    if cookie_value is None:
        return redirect('/register')
    else:
        return render_template('home.html', posts=posts)

@app.route('/register')
def register():
    return render_template('new_user.html')

@app.route('/handle_user', methods=['POST'])
def handle_user():
    name = request.form['namae']
    if name in users:
        return render_template('new_user.html', name=name)
    else:
        users.insert(0, name)
        with open('users.json', 'w') as u:
            json.dump(users, u)
        resp = make_response(redirect('/'))
        resp.set_cookie('username', name)
        return resp




@app.route('/handle_post', methods=['POST'])
def handle_post():
    title = request.form['title']
    now = datetime.now()
    formatted_time = now.strftime("%H:%M %d.%m.%Y")
    author = request.cookies.get('username')+" - "+formatted_time
    content = request.form['content']
    photo = request.files['photo']

    generating = True
    name = ""

    while generating:
        name = str(random.randint(10000000000000,99999999999999))+".jpg"
        if name in images:
            continue
        else:
            generating = False

    if photo and allowed_file(photo.filename):
        filename = name
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)
        posts.insert(0, {'title': title, 'author': author, 'content': content, 'photo': filename})
    else:
        posts.insert(0, {'title': title, 'author': author, 'content': content})


    with open('posts.json', 'w') as f:
        json.dump(posts, f)

    return redirect('/')


