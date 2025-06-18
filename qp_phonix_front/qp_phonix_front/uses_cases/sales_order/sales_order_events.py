import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr

import frappe
from frappe import _

def get_email_account_settings():
    """Obtiene la configuración de la cuenta de correo predeterminada de Frappe."""
    try:
        """
        Configuración de la cuenta de correo predeterminada:
        - email_id: Correo electrónico de la cuenta.
        - password: Contraseña de la cuenta (debe ser desencriptada).
        - domain: Dominio del correo electrónico.
        """
        email_account = frappe.db.get_value(
            "Email Account", {"default_outgoing": 1}, ["name","email_id", "password", "domain"], as_dict=True
        )
        if not email_account:
            frappe.log_error("No se encontró una cuenta de correo predeterminada.")
            return None

        email_account["password"] = frappe.utils.password.get_decrypted_password("Email Account", email_account["name"], fieldname="password")

        """
        Configuración del servidor SMTP para el dominio especificado en la cuenta de correo:
        - smtp_server: Servidor SMTP del dominio.
        """
        smtp_server = frappe.db.get_value(
            "Email Domain", email_account["domain"], ["email_server", "smtp_server", "smtp_port", "use_tls", "use_ssl_for_outgoing"], as_dict=True
        )
        if not smtp_server:
            frappe.log_error(f"No se encontró la configuración del dominio de correo: {email_account['domain']}")
            return None
        email_account["smtp_server"] = smtp_server["smtp_server"]
        email_account["smtp_port"] = smtp_server["smtp_port"]
        email_account["use_tls"] = smtp_server["use_tls"]
        email_account["use_ssl_for_outgoing"] = smtp_server["use_ssl_for_outgoing"]
        return email_account
    except Exception as e:
        frappe.log_error(f"Error al obtener la configuración de la cuenta de correo predeterminada: {str(e)}")
        return None
    
def get_sales_order_attachment(doc, attachments):
    """
    Función que obtiene el archivo adjunto del PDF de la orden de venta.
    """
    try:
        pdf_attachment = frappe.attach_print(
            doctype="Sales Order",
            name=doc.name,
            print_format="pdf-email",
            doc=doc
        )
        attachments.append(pdf_attachment)
        return attachments
    except Exception as e:
        frappe.log_error(f"Error al generar PDF de la orden de venta {doc.name}: {str(e)}")
        return attachments
    
def get_sales_order_additional_attachments(doc, attachments):
    try:
        file = frappe.db.get_value(
            "File",
            {"attached_to_doctype": "Sales Order", "attached_to_name": doc.name},
            ["file_url", "file_name", "name"],
            as_dict=True
        )
        if file:
            file_doc = frappe.get_doc("File", file["name"])
            file_content = file_doc.get_content()
            
            attachments.append({
                "fname": file_doc.file_name,
                "fcontent": file_content
            })
        return attachments
    except Exception as e:
        frappe.log_error(f"Error al obtener adjunto manual para {doc.name}: {str(e)}")
        return attachments
    
def get_sales_order_email_recipients(doc):
    """
    Función que obtiene los destinatarios del correo electrónico para la orden de venta.
    """
    recipients_set = set()
    
    if doc.get("contact_email"):
        recipients_set.add(doc.contact_email)
    
    if doc.get("owner"):
        owner_email = frappe.db.get_value("User", doc.owner, "email")
        if owner_email:
            recipients_set.add(owner_email)

    if doc.get("customer"):
        contacts = frappe.db.sql("""
            SELECT DISTINCT c.name
            FROM `tabContact` c
            INNER JOIN `tabDynamic Link` l ON l.parent = c.name
            WHERE l.link_doctype = 'Customer' AND l.link_name = %s
        """, (doc.customer,), as_dict=True)
        
        for c in contacts:
            contact = frappe.get_doc("Contact", c.name)
            if not contact.get("qp_is_recipient"):
                for email_id_row in contact.email_ids: 
                    if email_id_row.email_id:
                        recipients_set.add(email_id_row.email_id)
    
    return list(recipients_set)

def send_sales_order_confirmation_email(doc, method=None):
    """
    Función que se ejecuta por un doc_event para enviar un correo de confirmación de orden de venta.
    """

    if doc.status != "To Deliver and Bill":
        return

    old_doc = doc.get_doc_before_save()
    if not old_doc or old_doc.status == "To Deliver and Bill":
        return

    email_settings = get_email_account_settings()
    if not email_settings:
        return
    
    attachments = []
    attachments = get_sales_order_attachment(doc, attachments)
    attachments = get_sales_order_additional_attachments(doc, attachments)
    recipients = get_sales_order_email_recipients(doc)
    if not recipients:
        frappe.log_error(f"No se encontraron destinatarios para el correo de la orden de venta {doc.name}.")
        return
    to_addresses = [email for email in recipients if email]
    cc_addresses = ["gyepes@phoenixcontact.com", "jperez@phoenixcontact.com", "mvasquez@phoenixcontact.com"]
    if not to_addresses:
        return
    sender_email = email_settings["email_id"]
    sender_name = email_settings["name"]
    subject = _(f"Confirmación Orden de Venta {doc.name} / {doc.qp_phonix_reference}")
    message_html = f"""
    Buen día, estimado cliente,<br><br>
    Adjunto la confirmación de pedido de la orden de compra <strong>{doc.name}</strong>, con sus respectivas fechas de entrega. Favor comunicar la no aceptación o modificación de esta confirmación en un plazo de <strong>24 horas máximo</strong>.<br><br>
    """ 
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((sender_name, sender_email))
    msg["Subject"] = subject
    msg["To"] = ", ".join(to_addresses)
    if cc_addresses:
        msg["Cc"] = ", ".join(cc_addresses)
    msg.attach(MIMEText(message_html, "html"))
    if attachments:
        for attachment_data in attachments:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_data["fcontent"])
            encoders.encode_base64(part)
            
            filename = attachment_data.get("fname", f"{doc.name}.pdf")
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            msg.attach(part)
    smtp_server = email_settings["smtp_server"]
    smtp_port = email_settings["smtp_port"]
    smtp_username = email_settings["email_id"]
    smtp_password = email_settings["password"]
    use_tls = email_settings["use_tls"]
    use_ssl = email_settings["use_ssl_for_outgoing"]        
    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            if use_tls:
                server.starttls()

        server.login(smtp_username, smtp_password)
        
        all_recipients_for_smtp = to_addresses + cc_addresses
        server.sendmail(sender_email, all_recipients_for_smtp, msg.as_string())
        server.quit()
    except smtplib.SMTPAuthenticationError as e:
        frappe.log_error(f"Error de autenticación SMTP al enviar correo para SO {doc.name}: {str(e)}")
    except Exception as e:
        frappe.log_error(f"Error general al enviar correo directo para SO {doc.name}: {str(e)}")

def send_sales_order_modification_email(doc, method=None):
    """
    Función que se ejecuta por un doc_event para enviar un correo de modificación de orden de venta.
    """

    old_doc = doc.get_doc_before_save() 
    if not old_doc:
        return

    should_send_email = False

    if doc.status == "To Deliver and Bill" and old_doc.status == "To Deliver and Bill":
        if old_doc.delivery_date != doc.delivery_date:
            should_send_email = True
        else:
            old_items = {item.item_code: item for item in old_doc.items if item.item_code}
            for item in doc.items:
                if not item.item_code:
                    continue
                old_item = old_items.get(item.item_code)
                if old_item and old_item.delivery_date != item.delivery_date:
                    should_send_email = True
                    break
    
    if not should_send_email:
        return 

    email_settings = get_email_account_settings()
    if not email_settings:
        return

    attachments = []
    attachments = get_sales_order_attachment(doc, attachments)
    recipients  = get_sales_order_email_recipients(doc)
    if not recipients:
        frappe.log_error(f"No se encontraron destinatarios para el correo de la orden de venta {doc.name}.")
        return
    to_addresses = [email for email in recipients if email]
    cc_addresses = ["gyepes@phoenixcontact.com", "jperez@phoenixcontact.com", "mvasquez@phoenixcontact.com"]

    if not to_addresses:
        return

    sender_email = email_settings["email_id"]
    sender_name = email_settings["name"]
    subject = _(f"Modificación Fechas Orden de Compra {doc.name} / {doc.qp_phonix_reference}")
    message_html = f"""
    Buen día, estimado cliente,<br><br>
    Su orden de compra <strong>{doc.name}</strong> ha presentado cambios de fecha de entrega en algunos productos. Por favor, verifique el PDF adjunto, el cual contiene información detallada de estos cambios.<br><br>
    En caso de tener dudas, comuníquese con el personal de Ventas Internas y/o Ventas Externas.<br><br>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((sender_name, sender_email))
    msg["Subject"] = subject
    
    msg["To"] = ", ".join(to_addresses)
    if cc_addresses:
        msg["Cc"] = ", ".join(cc_addresses)

    msg.attach(MIMEText(message_html, "html"))

    if attachments:
        for attachment_data in attachments:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_data["fcontent"])
            encoders.encode_base64(part)
            
            filename = attachment_data.get("fname", f"{doc.name}.pdf")
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            msg.attach(part)

    smtp_server = email_settings["smtp_server"]
    smtp_port = email_settings["smtp_port"]
    smtp_username = email_settings["email_id"]
    smtp_password = email_settings["password"]
    use_tls = email_settings["use_tls"]
    use_ssl = email_settings["use_ssl_for_outgoing"]

    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            if use_tls:
                server.starttls()

        server.login(smtp_username, smtp_password)
        
        all_recipients_for_smtp = to_addresses + cc_addresses
        server.sendmail(sender_email, all_recipients_for_smtp, msg.as_string())
        server.quit()
        

    except smtplib.SMTPAuthenticationError as e:
        frappe.log_error(f"Error de autenticación SMTP al enviar correo para SO {doc.name}: {str(e)}")
    except Exception as e:
        frappe.log_error(f"Error general al enviar correo directo para SO {doc.name}: {str(e)}")

