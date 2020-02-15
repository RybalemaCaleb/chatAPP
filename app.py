from flask import Flask, render_template, request, make_response, redirect
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yf9te7237t273e76teXDuye*/*/338==2-'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manger = LoginManager()
login_manger.login_view = 'login'
login_manger.init_app(app)


@login_manger.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def isSame(p, pp):
    if p == pp:
        return True
    else:
        return False


def isStudent(reg):
    r = reg.lower()
    if r[0] != 'l':
        return True
    else:
        return False


def isNull(data):
    if data is None or data == "":
        return True
    else:
        return False


# def lens(limit, data, what):
#     if len(data) > limit:
#         return str(what) + " should be not more than " + str(limit) + " Characters"
#     else:
#         return True


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    regNo = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    dob = db.Column(db.String(15), nullable=False)
    firstname = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(25), nullable=False)
    yos = db.Column(db.Integer, nullable=False)
    studentno = db.Column(db.String(11))
    signup_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":

        firstname = request.form['firstname']
        surname = request.form['surname']
        regno = request.form['regno']
        studentno = request.form['studentno']
        dob = request.form['dob']
        yos = request.form['yos']
        password = request.form['password']
        cpassword = request.form['cpassword']

        if isNull(regno):
            message = "Registration number can't be left Empty"
            print(message)
            render_template('index.htm', message=message)

        if User.query.filter_by(regNo=regno).first() is not None:
            message = "Error: User Already Exists"
            print(message)
            return render_template('index.htm', message=message)
        password = password.strip()
        cpassword = cpassword.strip()
        if not isSame(password, cpassword):
            message = "Error: Passwords Should be the same"
            return render_template('index.htm', message=message)
        if len(password) < 8:
            message = "Error: Passwords Should be at least 8 Characters"
            return render_template('index.htm', message=message)

        if isStudent(regno):
            render_template('index.htm', message="Is Student")
            if isNull(studentno):
                message = "Error: Students should fill in the Student Number field"
                return render_template('index.htm', message=message)

            if User.query.filter_by(studentno=studentno).first() is not None:
                message = "Error: Student Already Exists"
                print(message)
                return render_template('index.htm', message=message)

            if isNull(yos):
                message = "Error: Students should fill in the Year of Study field"
                return render_template('index.htm', message=message)

        # noinspection PyArgumentList
        user = User(regNo=regno, password=bcrypt.generate_password_hash(password.encode('utf-8')), dob=dob,
                    firstname=firstname, surname=surname, yos=yos, studentno=studentno)
        db.session.add(user)
        db.session.commit()
        return render_template('login.htm', message="Registration Successful, You can now login!")
    return render_template('index.htm')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        reg = request.form['regno']
        password = request.form['password']

        if not (isNull(reg) or isNull(password)):
            user = User.query.filter_by(regNo=reg).first()
            if user is not None:
                if bcrypt.check_password_hash(user.password, password):
                    # resp = make_response(render_template('dashboad.htm'))
                    # resp.set_cookie("user_id", user.regNo)
                    login_user(user)
                    return redirect('dashboard')
                else:
                    render_template("login.htm", message="Login Failed, check Password")
        return render_template("login.htm", message="Login Failed, check  Registration Number and Password")

    return make_response(render_template('login.htm'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect('login')


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user

    data = {}
    data['Registration Number'] = user.regNo
    data['First Name'] = user.firstname
    data['Surname'] = user.surname
    student = False
    if isStudent(user.regNo):
        student = True
        data['Student Number'] = user.studentno
        data['Year of Study'] = user.yos

    data['Date of Birth'] = user.dob
    data['Registration Date'] = user.signup_date

    users = User.query.all()

    USERS = []

    for user in users:
        if isStudent(user.regNo) == student and user.regNo is not data['Registration Number']:
            USERS.append(user)

    return render_template('dashboad.htm', data=data, users=USERS, name=data['First Name'])


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
