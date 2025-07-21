# utils.py
import os
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings


def generate_invoice(order):
    from django.template.loader import get_template
    
    # Define the template path and output path
    template_path = "user/invoice_template.html"
    output_dir = os.path.join(settings.MEDIA_ROOT, "invoices")
    os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
    
    output_path = os.path.join(output_dir, f"invoice_{order.serial_number}.pdf")
    
    # Load template and render content
    template = get_template(template_path)
    context = {"order": order}
    html_content = template.render(context)
    
    # Write rendered content to a file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return output_path





