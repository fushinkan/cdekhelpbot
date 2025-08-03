from bot.states.customer import Customer, CUSTOMER_PROMPTS
from bot.states.invoice import InvoiceForm, INVOICE_PROMPTS


STATE_PROMPT_MAP = {
    Customer: CUSTOMER_PROMPTS,
    InvoiceForm: INVOICE_PROMPTS
}

async def get_prompt_for_state(state_obj):
    for cls, prompts in STATE_PROMPT_MAP.items():
        if state_obj.state in prompts:
            return prompts[state_obj.state]
    return None
