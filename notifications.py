import smtplib, ssl, config
import tulipy, numpy
context = ssl.create_default_context()
def email(messages):
    with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
        server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
        server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)

        email_message = "\n\n".join(messages)    
        server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_message)
        server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_SMS, email_message)

        server.quit()