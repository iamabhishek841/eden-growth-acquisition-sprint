# Measurement implementation spec

This document turns the proposed growth measurement design into an implementation checklist.

It is **not** a description of Eden Therapy Clinic's current analytics stack. It is the minimum instrumentation this portfolio case study would request before paid acquisition is scaled.

## 1. Naming standard

Every paid or partner link should use stable naming across the ad platform, landing page and reporting layer.

Example:

```text
utm_source=google
utm_medium=cpc
utm_campaign=deep_tissue_blackrock
utm_content=service_intent_v1
```

The exact taxonomy can change; consistency matters more than the labels themselves.

## 2. Event chain

```text
landing_view
→ service_cta_click
→ booking_start
→ booking_complete
→ appointment_complete
→ repeat_booking
```

Referral / partnership flows add:

```text
referral_booking
```

## 3. Required properties

| Event | Minimum useful properties |
| --- | --- |
| landing_view | source, medium, campaign, landing_page |
| service_cta_click | service, page, CTA label, source |
| booking_start | service, campaign, source, new/returning |
| booking_complete | service, campaign, source, revenue |
| appointment_complete | service, source, new/returning |
| repeat_booking | days since last visit, service, original source |
| referral_booking | partner/referral code, service, revenue |

## 4. Reconciliation principle

Ad-platform conversions should not be treated as the only source of truth.

A production workflow should reconcile:

```text
Ad platform
+ website / analytics events
+ booking / payment record
+ CRM / repeat-customer outcome
```

That makes it possible to distinguish a cheap lead from a valuable customer.

## 5. Weekly scorecard

The founder-facing weekly view should answer:

1. What did we spend?
2. How many qualified leads / booking starts did that create?
3. How many became completed bookings or customers?
4. What was CAC?
5. What revenue was attributable within the agreed attribution model?
6. Which sources produced attended / repeat customers?
7. Which experiment should be scaled, iterated or stopped?

## 6. Data-quality checks

Before decisions are made:

- confirm no duplicate booking IDs,
- verify spend and date ranges match the reporting period,
- check UTM/campaign naming drift,
- reconcile completed bookings with booking/payment records,
- separate new and returning customers,
- record cancellations/no-shows as a quality guardrail,
- document attribution-window assumptions.

## 7. What this spec does not claim

It does not claim:

- access to Eden's GA4, Search Console, Meta or Google Ads accounts,
- access to booking, payment or CRM data,
- that any proposed event already exists,
- that platform attribution is causal incrementality,
- that the demo CAC/ROAS thresholds match Eden's economics.
