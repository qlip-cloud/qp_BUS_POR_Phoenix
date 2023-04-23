import json
import os
import requests
import json
import uuid
import threading
import asyncio
import aiohttp
import frappe

@frappe.whitelist(allow_guest=True)
def handler(ApiKey, ApiSecret,ProductId,ServiceId,NIT= None,Nombre= None):

    code = generate_code()
    
    create_db_petition(code)

    payload = {
        "ApiKey": ApiKey, 
        "ApiSecret": ApiSecret,
        "ProductId": ProductId,
        "ServiceId":ServiceId,
        "NIT": NIT,
        "Nombre": Nombre
    }

    """asyncio.get_event_loop().run_until_complete(test(code, {
        "ApiKey": ApiKey, 
        "ApiSecret": ApiSecret,
        "ProductId": ProductId,
        "ServiceId":ServiceId,
        "NIT": NIT,
        "Nombre": Nombre
    }))"""

    frappe.enqueue(
        send_petition, # python function or a module path as string
        queue="default", # one of short, default, long
        #timeout=None, # pass timeout manually
        is_async=True, # if this is True, method is run in worker
        job_name="generate_report", # specify a job name
        #enqueue_after_commit=False, # enqueue the job after the database commit is done at the end of the request
        code = code, # kwargs are passed to the method as arguments
        payload = payload
    )
    

    #threading_emails = threading.Thread(target=send_petition, args = (code,payload))
    
    #threading_emails.start()
    
    return {
        'statusCode': 200,
        'code': code
    }
    
async def test(code, event):

    tasks = asyncio.create_task(send_petition(code, event))

    asyncio.wait([tasks])

def send_petition(code, payload):
    print("entre1")
    url = "https://devmasterdata-qa.azurewebsites.net/api/v1/administration/services/public/get/buy-report-public"

    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url,headers = headers, data=json.dumps(payload))
    print("entre2")
    
    """async with aiohttp.ClientSession() as session:
        print("entre")
        async with session.post(url,headers = headers, data=payload) as resp:
            print("hola")

            response = await resp.text()

            update_db_petition(code, response)
            print("chao")"""

    update_db_petition(code, response.text)

def create_db_petition(code):
    
    report = frappe.new_doc("qp_report")
    
    report.code = code
    
    report.insert()
    
def update_db_petition(code, response):
    
    report = frappe.get_doc("qp_report",code)
    
    report.response = response
    
    report.save()

def generate_code():

    return str(uuid.uuid1())
    
    
                       
    
    
