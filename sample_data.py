import pandas as pd
from datetime import date, timedelta
import random

def generate_sample_data(num_customers=6):
    customers = []

    base_date = date.today()

    for i in range(num_customers):
        usage = random.randint(0, 6)
        tickets = random.randint(0, 10)
        nps = random.randint(3, 10)

        customers.append({
            "customer_name": f"Sample Customer {i+1}",
            "usage_per_week": usage,
            "open_tickets": tickets,
            "nps": nps,
            "days_since_login": random.randint(0, 45),
            "contract_age_months": random.randint(1, 24),
            "usage_prev_period": max(0, usage + random.randint(-2, 2)),
            "open_tickets_prev_period": max(0, tickets + random.randint(-2, 2)),
            "nps_prev_period": max(0, min(10, nps + random.randint(-2, 2))),
            "renewal_date": (base_date + timedelta(days=random.randint(30, 180))).isoformat(),
            "contract_value": random.randint(3000, 25000),
        })

    return pd.DataFrame(customers)
