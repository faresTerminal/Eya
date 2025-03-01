from chargily_pay import ChargilyClient
from django.conf import settings

def get_chargily_client():
    # Check if the credentials are loaded correctly
    print("Chargily Key:", settings.CHARGILY_KEY)
    print("Chargily Secret:", settings.CHARGILY_SECRET)
    print("Chargily URL:", settings.CHARGILY_URL)

    return ChargilyClient(
        key=settings.CHARGILY_KEY,
        secret=settings.CHARGILY_SECRET,
        url=settings.CHARGILY_URL,  # Ensure this is the correct URL for the environment
    )



