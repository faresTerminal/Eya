from django import template
from deep_translator import GoogleTranslator

register = template.Library()

@register.filter
def translate_text(text, language_code='ar'):
    try:
        translator = GoogleTranslator(source="auto", target=language_code)
        translated_text = translator.translate(text)
    except Exception as e:
        # Handle translation errors
        translated_text = f"Translation error: {str(e)}"

    return translated_text




