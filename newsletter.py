"""
content
    - jokes
    - memes
    - inspirational quotes
        (from anime?)
        different language?
    - vocabulary
    - stats question & answer
    - forecast
    - reddit trending posts
email
    - recipients: list
    - send_time: time
    - format_message()
    - send_email()
GUI
    - config_content()
    - add_recipients()
    - remove_recipients()
    - schedule_time()
    - config_credentials()

- allow recipients to individually customize which content to include
    - types of quotes
- customize weather forecast location to each recipient
- customize send time based on recipient's time zone
- enrich word list
-

Admin-related enhancements
- indicate when certain content is unavailable
- save config settings between program runs
- enable running the program as a scheduled service
- store sensitive information in a secure format
"""
import content
import datetime as dt
from email.message import EmailMessage
import smtplib
import ssl
from decouple import config
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DailyDigestEmail:

    def __init__(self):
        self.content = {
            'quote': {'include': True, 'content': content.get_quote()},
            'reddit': {'include': True, 'content': content.get_reddit_post()},
            'word': {'include': True, 'content': content.get_random_word()},
        }
        self.recipient_list = config('EMAIL_RECIPIENTS')
        # self.sender_credentials = {'email': 'jyhuang.49@gmail.com',
        #                            'password': 'stay17YOUNG!'}
        self.sender_credentials = {'email': config('EMAIL_SENDER_ADDRESS'),
                                   'password': config('EMAIL_SENDER_PASSWORD')}

    """
    send email to recipients on the recipient list
    """

    def send_email(self):
        # https://myaccount.google.com/lesssecureapps?pli=1&rapt=AEjHL4ORqAydibAzDjzKxcesW3RC5K_uWtO8C-BQiSoSNO2jyhkhQkotHLsHzatPbORS25bpgKtGy6lV_tJ_ajzduOQubP6oCw
        # https://support.google.com/accounts/answer/6010255?hl=en&visit_id=637869949943339761-1092939860&p=less-secure-apps&rd=1#zippy=%2Cif-less-secure-app-access-is-on-for-your-account

        # build email message
        msg = EmailMessage()
        msg['Subject'] = f'Daily Digest - {dt.date.today().strftime("%B %-d, %Y")}'
        msg['From'] = self.sender_credentials['email']
        # msg['To'] = ', '.join(self.recipient_list)
        msg['To'] = self.recipient_list

        # add plaintext and HTML content
        msg_body = self.format_message()
        msg.set_content(msg_body['text'])
        msg.add_alternative(msg_body['html'], subtype='html')

        # secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(self.sender_credentials['email'],
                         self.sender_credentials['password'])
            server.send_message(msg)

    """
    generate email message body as plaintext and html
    """

    def format_message(self):
        text = f'  -=  -=  -=~*    Good Morning! Today is {dt.date.today().strftime("%B %-d, %Y")}    *~=-    =-  =-  \n\n\n'

        # format random quote
        if self.content['quote']['include'] and self.content['quote']['content']:
            text += '-=~*    Quote of the Day    *~=-\n\n'
            text += f'{self.content["quote"]["content"]["quote"]} - {self.content["quote"]["content"]["author"]}\n\n'

        # format word
        if self.content['word']['include'] and self.content['word']['content']:
            text += '-=~*    Phrases of the Day    *~=-\n\n'
            for type, details in self.content['word']['content'].items():
                text += f'{type}:\n'
                text += f'\t{details["phrase"]}\n'
                for i in details["definition"]:
                    text += f'\t\t{i}\n\n'

        # format reddit post
        if self.content['reddit']['include'] and self.content['reddit']['content']:
            text += '-=~*    Reddit of the Day    *~=-\n\n'
            text += f'{self.content["reddit"]["content"]["title"]}\n{self.content["reddit"]["content"]["url"]}\n\n'

        html = f"""<html>
        <body>
        <center>
            <h1>Good Morning! Today is {dt.date.today().strftime("%B %-d, %Y")}</h1>
        """
        # format random quote
        if self.content['quote']['include'] and self.content['quote']['content']:
            html += f"""
            <h2>Quote of the Day</h2>
            <i>{self.content["quote"]["content"]["quote"]}</i> - {self.content["quote"]["content"]["author"]}
            """

        # format word
        if self.content['word']['include'] and self.content['word']['content']:
            html += "<h2>Phrases of the Day</h2>"
            for type, details in self.content['word']['content'].items():
                html += f"""<h4>{type}: {details["phrase"]}</h4>"""
                for i in details["definition"]:
                    html += f'- {i}<br>'

        # format reddit post
        if self.content['reddit']['include'] and self.content['reddit']['content']:
            html += f"""
            <h2>Reddit of the Day</h2>
            <a href="{self.content["reddit"]["content"]["url"]}">{self.content["reddit"]["content"]["title"]}</a>
                    """

        html += """
        </center>
        </body>
        </html>
        """
        return {'text': text, 'html': html}


if __name__ == '__main__':
    email = DailyDigestEmail()

    logger.info('   - test email content formation')
    message = email.format_message()
    with open('message_text.txt', 'w', encoding='utf-8') as f:
        f.write(message['text'])
    with open('message_html.html', 'w', encoding='utf-8') as f:
        f.write(message['html'])

    logger.info('   - test sending email')
    email.send_email()
