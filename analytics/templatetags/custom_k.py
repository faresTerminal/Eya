# custom_K.py
from django import template

register = template.Library()

@register.filter(name='format_revenue')
def format_revenue(value, is_money=False):
    try:
        value = float(value)

        # If the value is greater than or equal to 10,000,000 (1 Billion)
        if value >= 10_000_000:
            return "{:.1f} Miliarde".format(value / 10_000_000)  # Converts to billions (Miliarde)
        
        # If the value is greater than or equal to 1,000,000 but less than 10,000,000
        elif value >= 1_000_000:
            return "{:.1f} M".format(value / 10_000)  # Converts to 100M for values in the millions
        
        # If the value is greater than or equal to 100,000 but less than 1,000,000
        elif value >= 100_000:
            return "{:.1f} M".format(value / 10_000)  # Converts to 10M for values in the hundred-thousands
        
        # If the value is greater than or equal to 10,000 but less than 100,000
        elif value >= 10_000:
            return "{:.1f} M".format(value / 10_000)  # Converts to 1M for values in the tens of thousands
        
        # If it's money, append "DA" at the end
        elif is_money:
            return "{:,.0f} DA".format(value)  # For monetary values, use commas and "DA"
        
        # For other numbers, show them normally
        else:
            return "{:,.0f}".format(value)  # For numbers, use commas
    except (ValueError, TypeError):
        return value

