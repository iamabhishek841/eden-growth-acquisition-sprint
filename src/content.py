"""Structured business context and growth hypotheses for the portfolio case study.

Public observations are separated from proposed strategy. Nothing in this module
should be read as Eden internal performance data.
"""

PUBLIC_CONTEXT = [
    {
        "observation": "Eden Therapy Clinic is publicly listed in Blackrock, Dublin and offers online booking.",
        "source": "https://www.edentherapyclinic.ie/",
    },
    {
        "observation": "The public pricing page lists massage treatments from €110 and multiple service durations.",
        "source": "https://www.edentherapyclinic.ie/pricing?category=massage-therapy",
    },
    {
        "observation": "The public packages page promotes signature wellbeing packages with approximately 10% savings.",
        "source": "https://www.edentherapyclinic.ie/packages",
    },
    {
        "observation": "The public gift-card page offers fixed-value and signature-experience gift vouchers.",
        "source": "https://www.edentherapyclinic.ie/gift-card",
    },
]

ACQUISITION_HYPOTHESES = [
    {
        "channel": "Google Search",
        "audience": "High-intent local searcher",
        "offer": "Deep Tissue Massage",
        "hypothesis": "Service-specific search traffic should convert better when the ad and landing page match the exact treatment intent.",
        "landing": "Dedicated Deep Tissue service / booking page",
        "primary_metric": "Completed booking",
        "business_metric": "CAC and booked revenue",
    },
    {
        "channel": "Google Search",
        "audience": "Pregnancy wellbeing searcher",
        "offer": "Pregnancy treatment",
        "hypothesis": "Specific pregnancy-treatment intent can be captured with a focused search campaign and reassurance-led landing experience.",
        "landing": "Pregnancy treatment page",
        "primary_metric": "Completed booking",
        "business_metric": "CAC and booked revenue",
    },
    {
        "channel": "Meta Paid Social",
        "audience": "Self-care / gift consideration",
        "offer": "Signature packages or gift voucher",
        "hypothesis": "Visual package-led creative can create demand before the customer has an exact treatment search in mind.",
        "landing": "Package or gift-voucher page",
        "primary_metric": "Purchase / booking",
        "business_metric": "ROAS and new-customer CAC",
    },
    {
        "channel": "Organic Search",
        "audience": "Local problem-aware searcher",
        "offer": "Service education plus booking CTA",
        "hypothesis": "Service pages that answer high-intent questions can capture non-paid demand and move visitors directly into booking.",
        "landing": "Intent-matched service page",
        "primary_metric": "Organic booking",
        "business_metric": "Organic assisted bookings",
    },
    {
        "channel": "Referral",
        "audience": "Existing satisfied customer + referred friend",
        "offer": "Trackable referral incentive",
        "hypothesis": "A simple referral proposition can turn trust from existing customers into lower-cost acquisition.",
        "landing": "Referral booking path",
        "primary_metric": "Referred booking",
        "business_metric": "Referral CAC and repeat rate",
    },
    {
        "channel": "Partnership",
        "audience": "Relevant local community",
        "offer": "Partner-specific introduction / package",
        "hypothesis": "Aligned local partners can generate qualified demand if each partner has a trackable landing path or code.",
        "landing": "Partner-specific landing page",
        "primary_metric": "Partner-attributed booking",
        "business_metric": "Partner CAC and customer quality",
    },
]

CAMPAIGN_BLUEPRINTS = {
    "High-intent treatment search": {
        "channel": "Google Search",
        "audience": "People actively searching for a specific treatment near Blackrock / Dublin",
        "message": "Match the search intent directly: treatment, location, transparent next step.",
        "creative": "Responsive search ad with service-specific headlines and booking CTA.",
        "landing": "Exact service page, not the generic homepage.",
        "follow_up": "Booking confirmation and post-visit lifecycle follow-up.",
        "primary_metric": "Completed bookings",
        "guardrail": "Cancellation / no-show rate",
    },
    "Signature package demand": {
        "channel": "Meta Paid Social",
        "audience": "People considering self-care or a wellbeing gift",
        "message": "Lead with the experience and package value rather than a generic brand message.",
        "creative": "Short-form treatment / experience story with one clear package CTA.",
        "landing": "Signature packages page with a single next action.",
        "follow_up": "Retarget high-intent visitors; follow up after purchase with booking guidance.",
        "primary_metric": "Package purchase / booking",
        "guardrail": "Refund / cancellation rate",
    },
    "Lapsed-customer reactivation": {
        "channel": "Email / CRM",
        "audience": "Previous customer who has not booked again within the selected window",
        "message": "Relevant next treatment or package based on prior behaviour, without over-messaging.",
        "creative": "Short lifecycle email with one recommended next action.",
        "landing": "Relevant service or booking page.",
        "follow_up": "Stop sequence after booking; suppress non-relevant messages.",
        "primary_metric": "Repeat booking",
        "guardrail": "Unsubscribe rate",
    },
    "Referral loop": {
        "channel": "Referral",
        "audience": "Existing customer after a completed appointment",
        "message": "Make referring a friend simple, trackable and easy to understand.",
        "creative": "Post-visit referral message + unique code or tagged link.",
        "landing": "Short referral booking path.",
        "follow_up": "Attribute both referred booking and future repeat behaviour.",
        "primary_metric": "Referred customers",
        "guardrail": "Incentive cost per acquired customer",
    },
}

SEO_OPPORTUNITIES = [
    {
        "search_intent": "deep tissue massage blackrock",
        "intent": "High commercial",
        "page": "Deep Tissue service page",
        "content_action": "Strengthen local/service relevance, treatment expectations, pricing and booking CTA.",
        "conversion": "Booking",
    },
    {
        "search_intent": "pregnancy massage dublin",
        "intent": "High commercial",
        "page": "Pregnancy treatment page",
        "content_action": "Answer safety/expectation questions within appropriate professional boundaries and keep booking path clear.",
        "conversion": "Booking",
    },
    {
        "search_intent": "massage blackrock",
        "intent": "Commercial category",
        "page": "Massage category page",
        "content_action": "Clarify treatment choices and route visitors to the most relevant service.",
        "conversion": "Service-page click → booking",
    },
    {
        "search_intent": "wellbeing gift voucher dublin",
        "intent": "Gift / purchase",
        "page": "Gift-card page",
        "content_action": "Clarify voucher choices, validity and purchase path.",
        "conversion": "Gift-card purchase",
    },
]

LIFECYCLE_STAGES = [
    {
        "stage": "New lead / high-intent visitor",
        "trigger": "Lead captured or high-intent action",
        "message": "Answer the immediate question and make the next booking step obvious.",
        "cta": "View treatment / book",
        "kpi": "Lead-to-booking conversion",
    },
    {
        "stage": "Booked customer",
        "trigger": "Booking completed",
        "message": "Confirm date, location and what the customer needs to know before arrival.",
        "cta": "Manage booking",
        "kpi": "Attendance / cancellation rate",
    },
    {
        "stage": "Post-visit",
        "trigger": "Completed appointment",
        "message": "Thank the customer, request feedback and provide one relevant next step.",
        "cta": "Feedback / next booking",
        "kpi": "30/60-day repeat booking",
    },
    {
        "stage": "Lapsed customer",
        "trigger": "No repeat booking after chosen window",
        "message": "Relevant, low-frequency reactivation based on prior service or interest.",
        "cta": "Return to booking",
        "kpi": "Reactivation rate",
    },
]

PARTNERSHIP_HYPOTHESES = [
    {
        "partner_type": "Fitness / movement studio",
        "shared_audience": "People already investing in physical wellbeing",
        "test": "Trackable introduction offer or educational collaboration",
        "measurement": "Partner-attributed bookings and CAC",
    },
    {
        "partner_type": "Pregnancy / parent community",
        "shared_audience": "People seeking relevant pregnancy wellbeing services",
        "test": "Educational referral collaboration with a dedicated booking path",
        "measurement": "Qualified referrals and booked customers",
    },
    {
        "partner_type": "Local employer / team wellbeing",
        "shared_audience": "Employees looking for wellbeing benefits or gifting",
        "test": "Pilot voucher/package partnership",
        "measurement": "Voucher purchases and repeat bookings",
    },
    {
        "partner_type": "Complementary local service",
        "shared_audience": "Customers with adjacent wellbeing needs",
        "test": "Mutual referral using tagged links / codes",
        "measurement": "Incremental referred customers",
    },
]

SPRINT_PLAN = [
    {
        "week": "Week 1 — Baseline",
        "goal": "Understand and instrument",
        "actions": "Map acquisition → landing → booking; agree KPI definitions; verify tracking; establish current baselines.",
        "decision": "Which funnel stage and channel deserve the first test?",
    },
    {
        "week": "Week 2 — Launch",
        "goal": "Run small controlled tests",
        "actions": "Launch one high-intent acquisition test, one conversion test and one low-cost retention/referral test.",
        "decision": "Are the tests producing enough signal to continue?",
    },
    {
        "week": "Week 3 — Diagnose",
        "goal": "Find the constraint",
        "actions": "Separate traffic problems from landing-page, lead-quality, booking or follow-up problems.",
        "decision": "Scale, iterate or stop each test.",
    },
    {
        "week": "Week 4 — Reallocate",
        "goal": "Put the next euro and hour in the best place",
        "actions": "Shift budget/time toward validated winners, document learning and queue the next experiment.",
        "decision": "What is the next highest-value growth question?",
    },
]


MEASUREMENT_PLAN = [
    {
        "event": "landing_view",
        "meaning": "Customer lands on a campaign / service page",
        "properties": "utm_source, utm_medium, utm_campaign, landing_page",
        "decision_use": "Traffic quality and campaign-to-page alignment",
    },
    {
        "event": "service_cta_click",
        "meaning": "Customer clicks the primary booking / purchase CTA",
        "properties": "service, page, cta_label, source",
        "decision_use": "Landing-page intent and CTA effectiveness",
    },
    {
        "event": "booking_start",
        "meaning": "Customer begins the booking / purchase flow",
        "properties": "service, source, campaign, new_or_returning",
        "decision_use": "High-intent conversion and funnel drop-off",
    },
    {
        "event": "booking_complete",
        "meaning": "Appointment / purchase is completed",
        "properties": "service, revenue, source, campaign",
        "decision_use": "Customer acquisition, CAC and conversion",
    },
    {
        "event": "appointment_complete",
        "meaning": "Booked customer attends / completes the service",
        "properties": "service, new_or_returning, source",
        "decision_use": "Customer quality and cancellation / no-show guardrail",
    },
    {
        "event": "repeat_booking",
        "meaning": "Existing customer books again",
        "properties": "days_since_last_visit, service, original_source",
        "decision_use": "Retention and acquisition-quality feedback",
    },
    {
        "event": "referral_booking",
        "meaning": "Booking is attributed to a referral / partner code",
        "properties": "referrer_type, partner_code, service, revenue",
        "decision_use": "Referral / partnership CAC and customer quality",
    },
]

KPI_GLOSSARY = [
    {"kpi": "CPL", "formula": "Spend / leads", "why_it_matters": "Cost of generating an interested prospect."},
    {"kpi": "Lead → customer", "formula": "Customers / leads", "why_it_matters": "Whether lead volume is turning into real customers."},
    {"kpi": "CAC", "formula": "Spend / customers", "why_it_matters": "Acquisition economics at the customer level."},
    {"kpi": "ROAS", "formula": "Attributed revenue / ad spend", "why_it_matters": "Revenue returned for paid-media spend; not profit."},
    {"kpi": "Repeat rate", "formula": "Repeat customers / customers", "why_it_matters": "Whether acquired customers come back."},
]


PAID_MEDIA_PLAYBOOKS = {
    "Google Search": {
        "objective": "Capture existing high-intent demand and convert it into completed bookings.",
        "structure": "Separate service-intent groups so keyword, ad copy and landing page stay aligned.",
        "examples": "Phrase/exact-style themes such as deep tissue massage Blackrock, massage Blackrock, pregnancy massage Dublin.",
        "exclusions": "Review irrelevant research/job/training intent and add negatives only after query evidence supports it.",
        "creative": "Service + location + clear booking next step; avoid exaggerated therapeutic or medical promises.",
        "landing": "Send traffic to the exact service page with treatment context, transparent pricing and one primary booking CTA.",
        "measurement": "Search term → click → booking start → completed booking → attended appointment → repeat behaviour.",
    },
    "Meta Paid Social": {
        "objective": "Create or capture consideration for packages, gifting and first-time bookings.",
        "structure": "Test a small number of distinct creative hypotheses rather than many minor variations at once.",
        "examples": "Experience-led package story, gift-oriented creative, treatment-expectation/reassurance creative.",
        "exclusions": "Do not infer or target sensitive health conditions; keep audience design broad, lawful and privacy-aware.",
        "creative": "Show the experience, value proposition and one next action; judge success on bookings/purchases rather than engagement.",
        "landing": "Match each creative promise to the relevant package, gift or service page instead of a generic homepage.",
        "measurement": "Creative → landing visit → booking/purchase → customer CAC/ROAS → repeat behaviour.",
    },
}


SOCIAL_CONTENT_PLAYS = [
    {
        "play": "Treatment-expectation short video",
        "audience_need": "Reduce uncertainty before a first visit",
        "format": "15–25 sec short-form video: what to expect → proof/reassurance → one booking CTA",
        "primary_metric": "Qualified landing visits / booking starts",
        "decision": "Repeat only if downstream booking intent improves, not just views.",
    },
    {
        "play": "Signature package / gifting story",
        "audience_need": "Make the experience and value easy to understand",
        "format": "Experience-led reel/carousel → package page",
        "primary_metric": "Package-page visits → purchase / booking",
        "decision": "Keep the creative angle only if it produces commercial intent.",
    },
    {
        "play": "Search-led expert Q&A",
        "audience_need": "Answer a high-intent customer question in plain language",
        "format": "Short answer → relevant service page → booking CTA",
        "primary_metric": "Organic landing sessions → completed bookings",
        "decision": "Turn repeated winning questions into SEO + social content clusters.",
    },
]
