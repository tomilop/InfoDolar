from datetime import datetime

class ExchangeRate:
    def __init__(self, base_currency: str = '', quote_currency: str = '', type: str = '', exchange_rate_sell: float = 0, exchange_rate_buy: float = 0, date: datetime | None = None, source: str = '') -> None:
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.type = type
        self.exchange_rate_sell = exchange_rate_sell
        self.exchange_rate_buy = exchange_rate_buy
        self.date = date
        self.source = source

    def __str__(self) -> str:
        m = ''
        m += f'1 {self.base_currency} {self.type} = {self.exchange_rate_sell} {self.quote_currency}\n'
        m += f'{self.date}\n'
        m += f'{self.source}'

        return m
    
    def to_text(self) -> str:
        m = ''
        m += f'*{self.base_currency} {self.type}*\n'
        m += f'${int(self.exchange_rate_sell)} - ${int(self.exchange_rate_buy)}\n'

        return m
    
    '''
    def is_empty(self) -> bool:
        return self.base_currency == '' or self.quote_currency == '' or self.date is None
    
    def is_not_empty(self) -> bool:
        return not self.is_empty()
    '''
    
    def is_newer_than(self, an_exchange_rate: 'ExchangeRate') -> bool:
        flag = False

        if self.date is not None and an_exchange_rate.date is not None:
            flag = self.date > an_exchange_rate.date

        return flag
    
    def is_older_than(self, an_exchange_rate: 'ExchangeRate') -> bool:
        return not self.is_newer_than(an_exchange_rate)
    
    def __eq__(self, another_exchange_rate: 'ExchangeRate') -> bool:
        return (self.base_currency == another_exchange_rate.base_currency) and (self.quote_currency == another_exchange_rate.quote_currency) and (self.type == another_exchange_rate.type)
    
    @classmethod
    def dolar_blue(cls):
        return cls(base_currency='USD', quote_currency='ARS', type='blue')
    
    @classmethod
    def dolar_oficial(cls):
        return cls(base_currency='USD', quote_currency='ARS', type='oficial')
    
    @classmethod
    def euro_blue(cls):
        return cls(base_currency='EUR', quote_currency='ARS', type='blue')
    
    @classmethod
    def euro_oficial(cls):
        return cls(base_currency='EUR', quote_currency='ARS', type='oficial')
    