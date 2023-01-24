import telebot
import telegram
import time
import pyairtable
import requests
import json
import pickle
import airtable

from airtable import *
from config_file import *
api_key = 'keyItMsd5dUq2nC0P'
airtable = Airtable('appfwHMDb5pQTDHf2', 'tblVtBtNbUCtHeHD7', api_key)
#print(airtable.get_all(view='viwH3IMrMUNdu51su',sort='fldZkl2V5on0bAbdH'))
print(airtable.search("You login in TG (reg)", 'Alpha_crucis')[0]['fields']['Как тебя зовут (имя и фамилия)'])
#https://airtable.com/appfwHMDb5pQTDHf2/tblVtBtNbUCtHeHD7/viwH3IMrMUNdu51su/fldZkl2V5on0bAbdH
#https://airtable.com/appfwHMDb5pQTDHf2/tblVtBtNbUCtHeHD7/viwH3IMrMUNdu51su/fldZkl2V5on0bAbdH
