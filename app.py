import mimetypes
from flask import (
    Flask, url_for, render_template,
    session, redirect, request, jsonify
)
from datetime import timedelta
from services.alphavantage import AlphaVantageService

app = Flask(__name__)
app.secret_key = "_&rv%+l$me%#@z&p-#rsyzv9$j4p8h#zpnjijc8qxt$*w!t=sr"
app.permanent_session_lifetime = timedelta(days=1)
mimetypes.add_type('application/javascript', '.mjs')

API_SESSION_KEY = 'api_key'
SESSION_MAX_LIFETIME = 1 # In days


@app.route('/companies/search/')
def search() -> str:
    if API_SESSION_KEY not in session.keys():
        return redirect(url_for('login'))
    
    api_key = session[API_SESSION_KEY]
    service = AlphaVantageService(api_key)
    keyword = request.args.get('keyword')
    data = service.get_companies(keyword)
    return jsonify(data)

@app.route('/companies/<symbol>/intraday/<interval>')
def intraday(symbol, interval) -> str:
    if API_SESSION_KEY not in session.keys():
        return redirect(url_for('login'))
    
    api_key = session[API_SESSION_KEY]
    service = AlphaVantageService(api_key)
    data = service.get_intraday(symbol, interval)
    return jsonify(data)


@app.route('/companies/<symbol>/weekly')
def weekly(symbol) -> str:
    if API_SESSION_KEY not in session.keys():
        return redirect(url_for('login'))
    
    api_key = session[API_SESSION_KEY]
    service = AlphaVantageService(api_key)
    data = service.get_weekly(symbol)
    return jsonify(data)

@app.route('/companies/<symbol>/daily')
def daily(symbol) -> str:
    if API_SESSION_KEY not in session.keys():
        return redirect(url_for('login'))
    
    api_key = session[API_SESSION_KEY]
    service = AlphaVantageService(api_key)
    data = service.get_daily(symbol)
    return jsonify(data)

@app.route('/companies/<symbol>/monthly')
def monthly(symbol) -> str:
    if API_SESSION_KEY not in session.keys():
        return redirect(url_for('login'))
    
    api_key = session[API_SESSION_KEY]
    service = AlphaVantageService(api_key)
    data = service.get_monthly(symbol)
    return jsonify(data)


@app.route('/companies/<symbol>/quote')
def quote(symbol) -> str:
    if API_SESSION_KEY not in session.keys():
        return redirect(url_for('login'))
    
    api_key = session[API_SESSION_KEY]
    service = AlphaVantageService(api_key)
    data = service.get_quote(symbol)
    return jsonify(data)


@app.route('/companies/<symbol>/indicators/<indicator>/<interval>')
def indicators(symbol, indicator, interval) -> str:
    if API_SESSION_KEY not in session.keys():
        return redirect(url_for('login'))
    
    api_key = session[API_SESSION_KEY]
    service = AlphaVantageService(api_key)
    data = service.get_indicators(symbol, indicator, interval)
    return jsonify(data)


@app.route('/', methods=['POST', 'GET'])
def login() -> str:
    if request.method == "POST":
        api_key = request.form[API_SESSION_KEY]
        session.permanent = True
        session[API_SESSION_KEY] = api_key
        return redirect(url_for('login'))
    else:
        if API_SESSION_KEY in session.keys():
            return render_template('index.html')
        return render_template('login.html', key=API_SESSION_KEY)


@app.route('/logout')
def logout() -> str:
    if API_SESSION_KEY in session.keys():
        session.pop(API_SESSION_KEY, None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)