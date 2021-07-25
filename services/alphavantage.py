import requests
from requests.models import Response
from requests.exceptions import ConnectTimeout

ConnectErrs  = (ConnectionError, ConnectionResetError, ConnectionRefusedError)

ALPHA_VANTAGE_HOST = 'https://www.alphavantage.co'


'''
    HttpServiceBase is base service, which will 
    hold & handle the requests made over HTTP protocol
'''
class HttpServiceBase:

    # Local session to support authorization if available
    session = None 

    # Default headers with application/json as content-type
    headers = { 
        'Content-Type': 'application/json'
    }

    '''
        Constructor
    '''
    def __init__(self) -> None:
        self.session = requests.Session()

    '''
        This request method is a wrapper on 
        top of the requests module's request and 
        defaults to GET as we are doing mostly GET requests
    '''
    def request(self, cmd, path, method='GET', data=None, json=None, headers=None) -> Response:
        url = f'{ALPHA_VANTAGE_HOST}/query?function={cmd}&{path}&apikey={self.API_KEY}'
        try:
            res = self.session.request(method, url, headers=headers, json=json, data=data)
            if res.status_code == 200:
                return res.json()
            
            return self.__error(res)
        except ConnectErrs as e:
            print(e)
            return self.__error_message("ERROR: Unable to reach the API server")
        except ConnectTimeout as e:
            print(e)
            return self.__error_message("ERROR: The API server return timeout error")
        
    def __error_message(self, message = 'Failed to load the data') -> dict:
        return {
            'message': message
        }
    
    def __error(self, res) -> dict:
        error_message = self.__error_message()
        try:
            return { **res.json(), **error_message }
        except Exception as e:
            print("WARNING", e)
            return error_message
    
    def get_info(self, data) -> dict:
        return data.get('Information', data.get('Note', data.get('Error Message', None)))
    
    '''
        Destructor
    '''
    def __del__(self) -> None:
        # TODO:: Need to logout the service when authentication enabled
        pass


'''
    The Alpha Vantage service, which will help to
    call the various types of data Alpha Vantage endpoints
'''
class AlphaVantageService(HttpServiceBase):

    '''
        Constructor
    '''
    def __init__(self, api_key) -> None:
        self.API_KEY = api_key

        # Invoke the base class constructor
        super().__init__()
    
    '''
        This method will query all companies based on keyword
    '''
    def get_companies(self, keyword) -> dict:
        path = f'keywords={keyword}'
        command = 'SYMBOL_SEARCH'
        res = self.request(command, path)
        return res.get('bestMatches', [])
    
    '''
        This method will query the intraday data based on symbol and interval
    '''
    def get_intraday(self, symbol, interval) -> dict:
        path = f'symbol={symbol}&interval={interval}'
        command = 'TIME_SERIES_INTRADAY'
        res = self.request(command, path)
        message = self.get_info(res)
        info = res.get('Meta Data', {})
        series = res.get(f'Time Series ({interval})', {})
        series = self.__format_series(series)
        return {
            'message': message,
            'info': info,
            'series': series
        }
    
    '''
        This method will query the weekly data based on the symbol
    '''
    def get_weekly(self, symbol) -> dict:
        path = f'symbol={symbol}'
        command = 'TIME_SERIES_WEEKLY'
        res = self.request(command, path)
        message = self.get_info(res)
        meta_data = res.get('Meta Data', {})
        series = res.get('Weekly Time Series', {})
        series = self.__format_series(series)
        return {
            'message': message,
            'info': meta_data,
            'series': series
        }
    
    '''
        This method will query the daily data based on the symbol
    '''
    def get_daily(self, symbol) -> dict:
        path = f'symbol={symbol}&outputsize=full'
        command = 'TIME_SERIES_DAILY'
        res = self.request(command, path)
        message = self.get_info(res)
        meta_data = res.get('Meta Data', {})
        series = res.get('Time Series (Daily)', {})
        series = self.__format_series(series)
        return {
            'message': message,
            'info': meta_data,
            'series': series
        }
    
    '''
        This method will query the monthly data based on the symbol
    '''
    def get_monthly(self, symbol) -> dict:
        path = f'symbol={symbol}'
        command = 'TIME_SERIES_MONTHLY'
        res = self.request(command, path)
        message = self.get_info(res)
        meta_data = res.get('Meta Data', {})
        series = res.get('Monthly Time Series', {})
        series = self.__format_series(series)
        return {
            'message': message,
            'info': meta_data,
            'series': series
        }
    
    '''
        This method will query the current quote details based on symbol
    '''
    def get_quote(self, symbol) -> dict:
        path = f'symbol={symbol}'
        command = 'GLOBAL_QUOTE'
        res = self.request(command, path)
        message = self.get_info(res)
        quote = res.get('Global Quote', {})
        return {
            'quote': quote,
            'message': message
        }
    
    '''
        This method will query the indicator details based on symbol, indicator and interval
    '''
    def get_indicators(self, symbol, indicator, interval) -> dict:
        path = f'symbol={symbol}&interval={interval}&time_period=10&series_type=open'
        res = self.request(indicator, path)
        message = self.get_info(res)
        meta_data = res.get('Meta Data', {})
        series = res.get(f'Technical Analysis: {indicator}', {})
        series = self.__format_series(series)
        return {
            'message': message,
            'info': meta_data,
            'series': series
        }
    
    '''
        This utility method will format/convert the timeline data
    '''
    def __format_series(self, series) -> list:
        return [{ **v, 'date': k } for k, v in series.items()]