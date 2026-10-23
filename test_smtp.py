import smtplib

s = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
s.set_debuglevel(1)
s.starttls()
s.login("sangokenny@gmail.com", "ticjyfleuddvplam")
print("Login OK")
s.quit()