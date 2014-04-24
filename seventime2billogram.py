import requests
from billogram_api import *
from datetime import date, timedelta
import json
import urllib

def get_index(seq, attr, value):
    return next(index for (index, d) in enumerate(seq) if d['_id'][attr] == value)

#create Seventime connection
url = 'http://app.seventime.se/loginFromApp'
data = {'username': '', 'password': ''}
headers = {'content-type': 'application/json'}
#create session
s=requests.Session()
ra=s.post(url, data=json.dumps(data), headers=headers)

#request finished workorders
workorder_params = {'user':'0', 'workOrderStatus':'300', 'groupingKey':'day','sortDirection':'desc'}
workorder_data=s.get('http://app.seventime.se/workorders',params=workorder_params, headers=headers)
workorders = json.loads(workorder_data.text)

#create Billogram SANDBOX connection
username = ''
authkey= ''
api = BillogramAPI(username, authkey, api_base='https://sandbox.billogram.com/api/v2')


for idx,workorder in enumerate(workorders):
	
	#get work order customer data
	data = s.get('http://app.seventime.se/customers/'+workorder['customer'], headers=headers)
	customer = json.loads(data.text)

	#customer and work order details variables
	email = customer['email']
	title = workorder['title']
	description=workorder['description']
	name=workorder['customerName']
	firstname = name.split(' ', 1)[0]
	completedDate = workorder['completedDate']
	checkList = workorder['checkLists']
	workorderid = workorder['_id']
	customerid = customer['_id']
	customernumber = customer['customerNumber']

	#get workorders that are not invoiced
	data = s.post('https://app.seventime.se/timereports/getUninvoicedSummary',data=json.dumps(full_data), headers=headers)
	timedata = json.loads(data.text)
	if(idx==len(timedata)):
		print "break"
		break

	index = get_index(timedata, "customer", customerid)
	totaltime = timedata[index]['totalTime']
	
	invoice_data = {
	# Specifying the recipient, must always be one from the database.
	'customer': {
	# On creation, only the customer_no can be specified.
	'customer_no': customernumber
	},
	# Specifying the items being invoiced for, can either be from the database or single-use ones
	'items': [
	{
	# This item specifies just an item_no, so it always uses one from the database.
	# If there is no item by this number, the call will fail since other mandatory
	# fields are then missing.
	# Note that item numbers are strings, they can contain non-numeric characters.
	'item_no': '0001',
	# You must always specify how many of each item is being invoiced for.
	'count': totaltime
	}
	],
	# The inovoicing currency must always be given, although currently only SEK is supported.
	'currency': 'SEK',
	# Have the due date be 35 days (5 weeks) in the future
	'due_date': (date.today() + timedelta(days=14)).isoformat()
	}

	result = api.billogram.create(invoice_data)
	print result
