
from cocktail.events import when
from cocktail.controllers import get_request_url
from cocktail.controllers.csrfprotection import (
    CSRFProtection,
    CSRFProtectionExemption
)


@when(CSRFProtection.deciding_injection)
def exempt_payment_urls(e):
    url = get_request_url()
    if url.path.segments and url.path.segments[0] == "payments":
        raise CSRFProtectionExemption()

