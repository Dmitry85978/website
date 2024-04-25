from flask import Flask, url_for, render_template, request, redirect
import sqlite3
import random

con = sqlite3.connect('game_list.sqlite')
cur = con.cursor()

result = cur.execute("""SELECT * FROM game_info""").fetchall()
data = []
for item in result:
    d = {}
    d['image'] = item[0]
    d['title'] = item[1]
    d['description'] = item[2]
    d['cost'] = item[3]
    data.append(d)

def add_receipt(user, game, quan, cost):
    con = sqlite3.connect('receipts.sqlite')
    cur = con.cursor()
    cur.execute("""INSERT INTO purchases (user, game, quantity, total) VALUES (?, ?, ?, ?)""", (user, game, quan, cost * quantity))
    con.commit()

def check_user(log, pas):
    con = sqlite3.connect('user.sqlite')
    cur = con.cursor()
    us_log = cur.execute("SELECT login FROM log_pas").fetchall()
    ind = -1
    for i in range(len(us_log)):
        if log in us_log[i]:
            ind = i
    if ind != -1:
        if pas in cur.execute("SELECT password FROM log_pas").fetchall()[ind]:
            return True
    return False

def add_user(log, pas):
    if not (check_user(log, pas)):
        con = sqlite3.connect('user.sqlite')
        cur = con.cursor()
        cur.execute("INSERT INTO log_pas (login, password) VALUES (?, ?)", (log, pas))
        con.commit()
        return True
    return False

reg = False

quantity = 1

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/offers')
def offers():
    return render_template('offers.html', oflist=data)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    global quantity
    game, img, cost = request.args.get('game'), request.args.get('img'), request.args.get('cost')
    if request.method == "POST":
        if request.form['submit_button'] == '+' and quantity < 10:
            quantity += 1
        if request.form['submit_button'] == '-' and quantity > 1:
            quantity -= 1
    return render_template('payment.html', game=game, img=img, quantity=quantity, cost=cost, costpur=str(int(cost)*quantity))

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    game, cost, units = request.args.get('game'), request.args.get('cost'), request.args.get('units')
    if request.method == "POST":
        if reg or check_user(request.form['login'], request.form['password']):
            add_receipt(request.form['login'], game, units, cost)
            return redirect(url_for('key'))
        else:
            return redirect(url_for('registration'))
    return render_template('purchase.html', game=game, cost=cost)

@app.route('/key', methods=['GET', 'POST'])
def key():
    keys = []
    global quantity
    for i in range(int(quantity)):
        k = str(random.randint(10000, 1000000)).rjust(7, '0')
        keys.append(k)
    return render_template('key.html', keys=keys)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    global reg
    if request.method == 'POST':
        if request.form['repeat_password'] == request.form['password']:
            if add_user(request.form['login'], request.form['password']):
                reg = True
                return render_template('registration.html', reg=reg, fr=request.form['login'])
            elif add_user(request.form['login'], request.form['password']):
                return render_template('registration.html', reg=reg, fr='')
    return render_template('registration.html', reg=reg, fr='')

@app.route('/entrance', methods=['GET', 'POST'])
def entrance():
    global reg
    if request.method == 'POST':
        if check_user(request.form['login'], request.form['password']):
            reg = True
    return render_template('entrance.html', reg=reg)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
