import json
import requests
import json
import uuid
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
        is_async=True, # if this is True, method is run in worker
        job_name="generate_report", # specify a job name
        code = code, # kwargs are passed to the method as arguments
        payload = payload
    )
    

    #threading_emails = threading.Thread(target=send_petition, args = (code,payload))
    
    #threading_emails.start()
    
    return {
        'statusCode': 200,
        'code': code
    }
    

def send_petition(code, payload):
    print("entre1")
    url = "https://devmasterdata-qa.azurewebsites.net/api/v1/administration/services/public/get/buy-report-public"

    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url,headers = headers, data=json.dumps(payload))
    print("entre2")

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
    
    
                       
    
    
