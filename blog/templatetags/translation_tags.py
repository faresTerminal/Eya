from django import template
from googletrans import Translator

register = template.Library()
translator = Translator()

@register.filter
def translate_text(text, language_code='ar'):
    try:
        # Translate the text to the specified language
        translated_text = translator.translate(text, dest=language_code).text
    except Exception as e:
        # Handle translation errors
        translated_text = f"Translation error: {str(e)}"

    return translated_text




