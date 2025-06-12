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
        email_account = frappe.db.get_value(
            "Email Account", {"default_outgoing": 1}, ["smtp_server", "smtp_port", "email_id", "password", "use_tls", "use_ssl", "name"], as_dict=True
        )
        if not email_account:
            frappe.log_error("No se encontró una cuenta de correo predeterminada.")
            return None

        email_account["password"] = frappe.utils.password.get_decrypted_password("Email Account", email_account["name"], fieldname="password")
        return email_account
    except Exception as e:
        frappe.log_error(f"Error al obtener la configuración de la cuenta de correo predeterminada: {str(e)}")
        return None
    
def send_sales_order_modification_email(doc, method=None):
    """
    Función que se ejecuta por un doc_event para enviar un correo de modificación de orden de venta.
    """
    frappe.log_error(f"Enviando correo de modificación de orden de venta para SO: {doc.name}")

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

    try:
        pdf_attachment = frappe.attach_print(
            doctype="Sales Order",
            name=doc.name,
            print_format="pdf-email",
            doc=doc
        )
        attachments = [pdf_attachment]
    except Exception as e:
        frappe.log_error(f"Error al generar PDF de la orden de venta {doc.name}: {str(e)}")
        attachments = []
        
    recipients_set = set()
    if doc.get("contact_email"):
        recipients_set.add(doc.contact_email)
    if doc.get("owner"):
        owner_email = frappe.db.get_value("User", doc.owner, "email")
        if owner_email:
            recipients_set.add(owner_email)

    if doc.get("customer"):
        frappe.log_error(f"Buscando contactos para el cliente: {doc.customer}")
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
    
    to_addresses = list(recipients_set)
    cc_addresses = ["hilaryjohana1@gmail.com"] 

    if not to_addresses:
        frappe.log_error(f"No se encontraron destinatarios para SO: {doc.name}. No se enviará el correo.")
        return

    frappe.log_error(f"Destinatarios TO: {to_addresses}")
    frappe.log_error(f"Destinatarios CC: {cc_addresses}")

    sender_email = email_settings["email_id"]
    sender_name = email_settings["name"]
    subject = _(f"Modificación Fechas Orden de Compra {doc.name} / {doc.qp_phonix_reference}")
    message_html = f"""
    Buen día, estimado cliente,<br><br>
    Su orden de compra **{doc.name}** ha presentado cambios de fecha de entrega en algunos productos. Por favor, verifique el PDF adjunto, el cual contiene información detallada de estos cambios.<br><br>
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
        frappe.log_error(f"Adjuntando {len(attachments)} archivos.")
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
    use_ssl = email_settings["use_ssl"]

    frappe.log_error(f"Intentando conectar al servidor SMTP: {smtp_server}:{smtp_port}")
    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            frappe.log_error("Usando SMTP_SSL.")
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            if use_tls:
                server.starttls()
                frappe.log_error("Usando starttls.")

        frappe.log_error("Iniciando sesión SMTP.")
        server.login(smtp_username, smtp_password)
        frappe.log_error("Sesión SMTP iniciada exitosamente.")
        
        all_recipients_for_smtp = to_addresses + cc_addresses
        frappe.log_error(f"Enviando correo desde '{sender_email}' a '{all_recipients_for_smtp}'")
        server.sendmail(sender_email, all_recipients_for_smtp, msg.as_string())
        server.quit()
        
        frappe.log_error(f"Correo directo enviado exitosamente para SO: {doc.name}") 

    except smtplib.SMTPAuthenticationError as e:
        frappe.log_error(f"Error de autenticación SMTP al enviar correo para SO {doc.name}: {str(e)}")
    except Exception as e:
        frappe.log_error(f"Error general al enviar correo directo para SO {doc.name}: {str(e)}")

