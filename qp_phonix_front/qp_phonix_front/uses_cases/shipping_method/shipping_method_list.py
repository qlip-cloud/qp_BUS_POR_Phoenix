import frappe
from frappe import _
from frappe.utils import getdate, get_datetime
from erpnext.controllers.website_list_for_contact import get_customers_suppliers
import datetime


WEEKDAYS = {

    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
} # index of python

WEEKDAYS_JS = {
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6,
    "Sunday": 0
} # index of javascript


@frappe.whitelist()
def vf_shipping_method_list():
    
    try:

        customer = __get_customer()

        shipping_method_list = []

        shipping_method_ids = list(map(lambda item: item.shipping_method,customer.gp_shipping_method)) 
        shipping_method_ids = str(shipping_method_ids).replace("[","(").replace("]",")")
        filters = {
            "name": ["in", shipping_method_ids]
        }
        
        sql = """
            SELECT
                name,
                IF(description IS NULL or description = '', name,  description) as description,
                IF(tooltip IS NULL or tooltip = '', name,  tooltip) as tooltip
            FROM
                tabqp_GP_ShippingType
            WHERE
                name in {}

        """.format(shipping_method_ids)

        so_list = frappe.db.sql(sql, as_dict=1)

        return so_list        

    except Exception as error:

        shipping_method_list = []

        frappe.log_error(message=error, title="Shipping Method List")

        pass

    return shipping_method_list


@frappe.whitelist()
def vf_shipping_date_list(shipping_method, days=42):

    try:

        active_dates = __get_active_days(shipping_method)

        result_dates = __get_date_list(active_dates, days)

    except Exception as error:

        result_dates = []

        frappe.log_error(message=error, title="Shipping date List")

        pass

    return result_dates



def __get_customer():
    
    user = frappe.session.user

    # find party for this contact
    customers, suppliers = get_customers_suppliers('Sales Order', user)

    if len(customers) < 1:

        frappe.throw(_("User does not have an associated client"))

    customer = frappe.get_doc('Customer', customers[0])

    return customer


def __get_active_days(shipping_method):

    active_date_list = frappe.db.get_list('qp_GP_WeeklySchedule',
        filters={
            'parent': shipping_method,
            'enabled': 1
        },
        fields=['day', 'delivery_time', 'cut_off'],
        order_by="idx"
    )

    active_dates = {}
    
    for item in active_date_list:

        active_dates[item.day] = item.delivery_time - datetime.timedelta(minutes=item.cut_off*60)

    return active_dates

def __get_date_list(active_dates, days):

    rec_now = rec_now_day = get_datetime()

    result_dates = []

    result = {}

    indx = 1

    while indx <= days:

        day_of_week = getdate(rec_now_day)

        day_rec = WEEKDAYS[day_of_week.weekday()]

        if day_rec in active_dates.keys():

            date_to_compare = __get_delta_time(rec_now_day, active_dates[day_rec])

            if rec_now <= date_to_compare:

                result_dates.append(getdate(rec_now_day).strftime('%Y-%m-%d'))

        rec_now_day += datetime.timedelta(days=1)

        indx += 1

    result = {
        'weekdaysenabled': [WEEKDAYS_JS[ind] for ind in active_dates.keys()],
        'mindate': result_dates and min(result_dates) or None,
        'maxdate': None
    }

    return result


def __get_delta_time(rec_now_day, active_dates_day):

    down_day = rec_now_day + datetime.timedelta(days=active_dates_day.days)

    delta_count_down = active_dates_day

    if active_dates_day.days < 0:
        delta_count_down = active_dates_day +  datetime.timedelta(days=abs(active_dates_day.days))

    dev_time = (datetime.datetime.min + delta_count_down).time()

    return datetime.datetime(
        down_day.year,
        down_day.month,
        down_day.day,
        dev_time.hour,
        dev_time.minute,
        dev_time.second,
        0
    )
