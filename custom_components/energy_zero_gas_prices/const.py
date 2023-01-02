
from datetime import timedelta

DOMAIN = "energy_zero_gas_prices"

ATTRIBUTION = "Data provided by Energy Zero API"
ICON = "mdi:currency-eur"
UNIQUE_ID = f"{DOMAIN}_component"
COMPONENT_TITLE = "Gas prices"

BASE_API_URL = 'https://api.energyzero.nl/v1/energyprices'
UPDATE_INTERVAL = timedelta(hours=1)
