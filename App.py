import requests
import json
from datetime import datetime
from ExchangeRate import ExchangeRate

from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

class App:
    def __init__(self) -> None:
        settings = open('config.json', mode='r')
        data = json.load(settings)

        self.url_source: str = data['url_api']
        self.token_telegram: Final = data['token_telegram']
        self.bot_username: Final = data['bot_username']
        self.exchange_rates: list = list()

    def get_raw_exchange_rates(self):
        try:
            response = requests.get(self.url_source)

            if response.status_code == 200:
                data = response.json()
            else:
                data = None
                self.print_in_console(f'No fué posible descargar los datos de {response.url}.')

        except Exception as e:
            self.print_in_console(f'Error: {e}.')
            data =  None

        return data

    @staticmethod
    def print_in_console(text: str) -> None:
        time = datetime.now()
        hour = time.hour
        minute = time.minute

        if time.minute < 10:
            minute = f'0{time.minute}'

        print(f'{hour}:{minute}. {text}')

    def get_exchange_rates(self) -> None:
        raw = self.get_raw_exchange_rates()
        self.exchange_rates = list()

        if raw is not None:
            source = 'Bluelytics'

            date = raw['last_update']
            date = datetime.fromisoformat(date)

            cotizacion_dolar_oficial_venta = raw['oficial']['value_sell']
            cotizacion_dolar_oficial_compra = raw['oficial']['value_buy']
            dolar_oficial = ExchangeRate('USD', 'ARS', 'oficial', cotizacion_dolar_oficial_venta, cotizacion_dolar_oficial_compra, date, source)
            self.exchange_rates.append(dolar_oficial)

            cotizacion_dolar_blue_venta = raw['blue']['value_sell']
            cotizacion_dolar_blue_compra = raw['blue']['value_buy']
            dolar_blue = ExchangeRate('USD', 'ARS', 'blue', cotizacion_dolar_blue_venta, cotizacion_dolar_blue_compra, date, source)
            self.exchange_rates.append(dolar_blue)

            cotizacion_euro_oficial_venta = raw['oficial_euro']['value_sell']
            cotizacion_euro_oficial_compra = raw['oficial_euro']['value_buy']
            euro_oficial = ExchangeRate('EUR', 'ARS', 'oficial', cotizacion_euro_oficial_venta, cotizacion_euro_oficial_compra, date, source)
            self.exchange_rates.append(euro_oficial)

            cotizacion_euro_blue_venta = raw['blue_euro']['value_sell']
            cotizacion_euro_blue_compra = raw['blue_euro']['value_buy']
            euro_blue = ExchangeRate('EUR', 'ARS', 'blue', cotizacion_euro_blue_venta, cotizacion_euro_blue_compra, date, source)
            self.exchange_rates.append(euro_blue)

    def exist(self, an_exchange_rate):
        flag = False

        if len(self.exchange_rates) != 0:
            for exchange_rate in self.exchange_rates:
                if exchange_rate == an_exchange_rate:
                    flag = True
                    break
        
        return flag

    def search(self, an_exchange_rate) -> 'ExchangeRate':
        item = None

        for exchange_rate in self.exchange_rates:
            if an_exchange_rate == exchange_rate:
                item = exchange_rate
                break

        return item
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message is not None:
            await update.message.reply_text('Hola!')

    async def dollar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message is not None:
            self.print_in_console(f'User: {update.message.text}')

            self.get_exchange_rates()
            exchange_rate = self.search(ExchangeRate.dolar_blue())

            if exchange_rate is not None:
                text = exchange_rate.to_text()
            else:
                text = 'aea'
            self.print_in_console(f'InfoDolar: {text}')
            await update.message.reply_text(text, parse_mode='MARKDOWN')

    async def euro_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message is not None:
            self.print_in_console(f'User: {update.message.text}')

            self.get_exchange_rates()
            exchange_rate = self.search(ExchangeRate.euro_blue())

            if exchange_rate is not None:
                text = exchange_rate.to_text()
            else:
                text = 'aea'

            self.print_in_console(f'InfoDolar: {text}')
            await update.message.reply_text(text, parse_mode='MARKDOWN')

    async def error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.print_in_console(f'Update {update} caused error {context.error}')

    def initialize(self):
        self.print_in_console('Iniciando...')
        app = Application.builder().token(self.token_telegram).build()

        #commands
        app.add_handler(CommandHandler('start', self.start_command))
        app.add_handler(CommandHandler('dolar', self.dollar_command))
        app.add_handler(CommandHandler('euro', self.euro_command))

        #messages
        app.add_handler(MessageHandler(filters.TEXT, self.handle_message))

        #errors
        app.add_error_handler(self.error)

        self.print_in_console('Sondeando...\n')
        app.run_polling(poll_interval=1)

    def handle_response(self, text: str) -> str | None:
        text_procesed: str = text.lower()
        response = None

        if 'oficial' in text_procesed:
            if 'dolar' in text_procesed:
                self.get_exchange_rates()
                exchange_rate = self.search(ExchangeRate.dolar_oficial())
                response = exchange_rate.to_text()
            elif 'euro' in text_procesed and 'oficial' in text_procesed:
                self.get_exchange_rates()
                exchange_rate = self.search(ExchangeRate.euro_oficial())
                response = exchange_rate.to_text()
        else:
            if 'dolar' in text_procesed:
                self.get_exchange_rates()
                exchange_rate = self.search(ExchangeRate.dolar_blue())
                response = exchange_rate.to_text()
            elif 'euro' in text_procesed:
                self.get_exchange_rates()
                exchange_rate = self.search(ExchangeRate.euro_blue())
                response = exchange_rate.to_text()

        return response

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_type: str = update.message.chat.type
        text: str = update.message.text

        self.print_in_console(f'{update.message.chat.username} in {message_type}: {text}')

        if message_type == 'group' or message_type == 'supergroup':
            if self.bot_username in text:
                new_text: str = text.replace(self.bot_username, '').strip()
                response: str = self.handle_response(new_text)
            else:
                return
        else:
            response: str = self.handle_response(text)
        
        self.print_in_console(f'Bot: {response}')
        await update.message.reply_text(response, parse_mode='MARKDOWN')


if __name__ == '__main__':
    app = App()
    app.initialize()