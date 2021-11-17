#!/usr/bin/python3
import time
import RPi.GPIO as GPIO
import os
import re
import codecs
import subprocess
from subprocess import *
from time import sleep, strftime
from datetime import datetime

# Zuordnung der GPIO Pins (ggf. anpassen)
LCD_RS = 4
LCD_E  = 17
LCD_DATA4 = 18
LCD_DATA5 = 22
LCD_DATA6 = 23
LCD_DATA7 = 24

LCD_WIDTH = 20 		# Zeichen je Zeile
LCD_LINE_1 = 0x80 	# Adresse der ersten Display Zeile
LCD_LINE_2 = 0xC0 	# Adresse der zweiten Display Zeile
LCD_LINE_3 = 0x94
LCD_LINE_4 = 0xD4
LCD_CHR = GPIO.HIGH
LCD_CMD = GPIO.LOW
E_PULSE = 0.0005
E_DELAY = 0.0005

def lcd_send_byte(bits, mode):
   # Pins auf LOW setzen
  GPIO.output(LCD_RS, mode)
  GPIO.output(LCD_DATA4, GPIO.LOW)
  GPIO.output(LCD_DATA5, GPIO.LOW)
  GPIO.output(LCD_DATA6, GPIO.LOW)
  GPIO.output(LCD_DATA7, GPIO.LOW)
  if bits & 0x10 == 0x10:
    GPIO.output(LCD_DATA4, GPIO.HIGH)
  if bits & 0x20 == 0x20:
    GPIO.output(LCD_DATA5, GPIO.HIGH)
  if bits & 0x40 == 0x40:
    GPIO.output(LCD_DATA6, GPIO.HIGH)
  if bits & 0x80 == 0x80:
    GPIO.output(LCD_DATA7, GPIO.HIGH)
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, GPIO.HIGH)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, GPIO.LOW)
  time.sleep(E_DELAY)
  GPIO.output(LCD_DATA4, GPIO.LOW)
  GPIO.output(LCD_DATA5, GPIO.LOW)
  GPIO.output(LCD_DATA6, GPIO.LOW)
  GPIO.output(LCD_DATA7, GPIO.LOW)
  if bits&0x01==0x01:
    GPIO.output(LCD_DATA4, GPIO.HIGH)
  if bits&0x02==0x02:
    GPIO.output(LCD_DATA5, GPIO.HIGH)
  if bits&0x04==0x04:
    GPIO.output(LCD_DATA6, GPIO.HIGH)
  if bits&0x08==0x08:
    GPIO.output(LCD_DATA7, GPIO.HIGH)
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, GPIO.HIGH)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, GPIO.LOW)
  time.sleep(E_DELAY)

def display_init():
  lcd_send_byte(0x33, LCD_CMD)
  lcd_send_byte(0x32, LCD_CMD)
  lcd_send_byte(0x28, LCD_CMD)
  lcd_send_byte(0x0C, LCD_CMD)
  lcd_send_byte(0x06, LCD_CMD)
  lcd_send_byte(0x01, LCD_CMD)

def run_cmd(cmd):
  p = Popen(cmd, shell=True, stdout=PIPE)
  output = p.communicate()[0]
  return str(output)

def lcd_message(message):
  message = message.ljust(LCD_WIDTH)
  for i in range(LCD_WIDTH):
    m = message[i]
    o = ord(m)
    lcd_send_byte(int(o), LCD_CHR)

if __name__ == '__main__':
  # initialisieren
  GPIO.setmode(GPIO.BCM)
  GPIO.setwarnings(False)
  GPIO.setup(LCD_E, GPIO.OUT)
  GPIO.setup(LCD_RS, GPIO.OUT)
  GPIO.setup(LCD_DATA4, GPIO.OUT)
  GPIO.setup(LCD_DATA5, GPIO.OUT)
  GPIO.setup(LCD_DATA6, GPIO.OUT)
  GPIO.setup(LCD_DATA7, GPIO.OUT)

  display_init()

  ipeth0 = run_cmd("ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1 | head -n1 | tr -d \'\n\'")
  ipeth0 = "eth0 " + str(ipeth0)
  lcd_send_byte(LCD_LINE_1, LCD_CMD)
  lcd_message(ipeth0)
#	ipwlan0 = run_cmd("ip addr show wlan0 | grep inet | awk '{print $2}' | cut -d/ -f1 | head -n1 | tr -d \'\n\'")
#	ipwlan0 = "wl0 " + ipwlan0
#	lcd_send_byte(LCD_LINE_2, LCD_CMD)
#	lcd_message(ipwlan0)

  time.sleep(2)

  lcd_send_byte(LCD_LINE_1, LCD_CMD)
  lcd_message("Es scheint zu")
  lcd_send_byte(LCD_LINE_2, LCD_CMD)
  lcd_message("funktionieren :)")

  time.sleep(2)

  i = 0

  while i < 10:
    title = subprocess.run(['mpc', 'current'], stdout=subprocess.PIPE).stdout.decode('ascii',errors='ignore')
    title = re.sub(r'[^\x00-\x7f]',r'', title)
    title = re.sub("\n|\r", "", title)
    lcd_send_byte(LCD_LINE_1, LCD_CMD)
    lcd_message(title[0:20])
    lcd_send_byte(LCD_LINE_2, LCD_CMD)
    lcd_message(title[20:40])
    lcd_send_byte(LCD_LINE_3, LCD_CMD)
    lcd_message(title[40:60])
    lcd_send_byte(LCD_LINE_4, LCD_CMD)
    lcd_message(title[60:80])
    time.sleep(1)
#		i+= 1

  GPIO.cleanup()
