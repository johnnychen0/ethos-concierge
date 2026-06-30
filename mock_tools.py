"""
mock_tools.py — fake "backend" for the Welcome-Back Concierge demo.

Each function below stands in for a real Ethos system (CRM, quoting engine, etc.).
They return hardcoded/computed data so the agent works with NO real backend.
The model never knows it's mocked — it just calls the tool and gets data back.
"""

# ---- Fake database (one returning user: Sarah) ----------------------------
USERS = {
    "sarah_001": {
        "name": "Sarah",
        "age": 45,
        "state": "CA",
        "email": "sarah@example.com",
        "dependents": 2,
        "has_mortgage": True,
        "income_band": "$100k-150k",
    }
}

CONTEXT = {
    "sarah_001": {
        "sentiment": "hesitant_but_engaged",
        "frustration_level": "low",
        "prior_sessions": 2,
        "last_topics": ["term vs whole", "is 20-year enough", "monthly cost"],
    }
}

APPLICATIONS = {
    "sarah_001": {
        "stage": "dropped_off",
        "last_step": "final_review",
        "plan_in_progress": "term",
        "coverage_amount": 500000,
        "term_length": 20,
    }
}


# ---- READ tools (safe; agent may call these freely) -----------------------
def get_user_profile(user_id):
    """Who the user is — name, age, state, household details."""
    return USERS.get(user_id, {})


def get_customer_context(user_id):
    """CDP signals — sentiment, frustration, prior conversation topics."""
    return CONTEXT.get(user_id, {})


def get_application_status(user_id):
    """Where the user is in the funnel and where they dropped off."""
    return APPLICATIONS.get(user_id, {"stage": "none"})


# Fictitious-but-realistic product names for the demo (not real Ethos products)
PLAN_NAMES = {"term": "Ethos SmartTerm", "whole": "Ethos Lifelong Whole Life"}


def get_plan_options(state):
    """Products available in the user's state (compliance: state-specific)."""
    return [
        {"plan_type": "term",  "name": PLAN_NAMES["term"],  "term_lengths": [10, 20, 30], "coverage_range": [100000, 2000000]},
        {"plan_type": "whole", "name": PLAN_NAMES["whole"], "term_lengths": None,         "coverage_range": [25000, 1000000]},
    ]


def get_quote(age, coverage, term_length, plan_type):
    """Illustrative monthly price. (Toy formula — NOT real underwriting.)"""
    base = (coverage / 1000) * 0.10 * (age / 40)
    if plan_type == "term":
        monthly = base * (term_length / 20)
    else:  # whole life is far pricier (builds cash value)
        monthly = base * 10
    monthly = round(monthly, 2)
    return {
        "plan_type": plan_type,
        "plan_name": PLAN_NAMES.get(plan_type, plan_type),
        "coverage": coverage,
        "term_length": term_length,
        "monthly_premium": monthly,
        "annual_premium": round(monthly * 12, 2),
        "note": "Illustrative estimate, not a binding quote.",
    }


def get_promotions(user_id):
    """Promotions the user is eligible for."""
    return [{"promo": "First month free", "discount": "1 month", "eligibility": "new applicants"}]


# ---- ACTION tools (side effects; require explicit user "yes") --------------
def submit_application(user_id, plan_type, coverage, term_length):
    """Submit the application. Only call after the user explicitly confirms."""
    return {"confirmation_id": "APP-48213", "status": "submitted",
            "plan_type": plan_type, "coverage": coverage, "term_length": term_length}


def escalate_to_human(context_package):
    """Queue a callback from a licensed human rep. NOT emergency dispatch."""
    return {"ticket_id": "ESC-7791", "queue": "licensed_agents",
            "channel": "phone/chat callback", "callback_eta_minutes": 4,
            "note": "A licensed Ethos rep will follow up by phone or chat. "
                    "This is NOT emergency dispatch or a visit to the user's location."}
