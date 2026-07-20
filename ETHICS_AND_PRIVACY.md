# ETHICS_AND_PRIVACY.md

This project concerns the reported illnesses and, in at least one publicly reported case,
the death of a child. The families involved are identifiable in public coverage and are
living through the worst thing that can happen to a family. Everything below is written
with that fact in the foreground.

## 1. Absolute prohibitions

The platform and everyone working on it must **never**:

- Identify or attempt to infer **individual children** in any structured data, map, or
  chart.
- Publish or store **exact residential addresses** or residential coordinates of affected
  or any private families.
- Infer the **school, park, daycare, sports team, or daily routine** of a specific child
  from social media, photographs, uniforms, or family accounts.
- **Scrape private profiles** or take any step toward **deanonymizing** families.
- Engage in **medical speculation about any named individual**.
- **Fabricate** data, **silently fill** missing values, or **invent** patient information.
- Present the platform's outputs as a diagnosis, medical advice, or a causal finding.

## 2. Health data is aggregate-only

Publicly reported health events are stored in a registry called **PUBLICLY REPORTED HEALTH
EVENTS**, not a medical case registry. Each entry captures only what a lawful public source
explicitly states, and only at an aggregated level:

- Reported diagnosis (e.g., "Ewing sarcoma"), approximate age or age range, approximate
  year of diagnosis, community association ("associated with Ladera Ranch").
- A boolean `names_individual` recording *whether the source named a person* — **the name
  itself is never stored.**
- Medical verification status, which defaults to **"not independently verified"** unless an
  official registry or medical source states otherwise.

We never geocode an individual event to a residence. Spatial analysis is done on
population zones and site locations, never on patient homes.

## 3. Named individuals in narrative context

Public coverage names some individuals, including a teenager who died. A research platform
does not need to repeat names to do its work, and does not. Where a source must be
described, we refer to "a publicly reported case" and cite the source. We do not build a
searchable index of named patients. We do not reproduce photographs of sick children.

## 4. Why aggregation is not just legal caution

Beyond privacy law, deanonymization would (a) expose grieving families to harassment,
(b) create pressure to interpret individual tragedies as proof of a hypothesis, which is
exactly the bias this project is built to resist, and (c) risk turning a research tool into
an instrument that assigns blame before evidence supports it.

## 5. Data retention & security

- No individual-level medical, address, or identity data is collected or retained. If a
  future, lawful, consented, IRB-approved phase ever handles individual-level data, it must
  live in a separately governed, access-controlled store — never in this public platform.
- Raw downloads and any sensitive interim files are git-ignored (`data/raw/*`) and are not
  committed.
- Source archives store public documents only.

## 6. IRB / human-subjects posture

The current phase uses only public, already-published, aggregate information and involves
no interaction with human subjects, so it is not human-subjects research requiring IRB
review. **Any** later phase that contacts families, collects individual health information,
or reconstructs individual exposure **does** require IRB review, informed consent, and (for
medical verification) proper authorized channels. These are logged as final-stage evidence
gates, not undertaken here.

## 7. Community sensitivity

- No "hotspot" or fear-based graphics without valid statistical support.
- Language stays measured; the platform never tells families their community caused their
  child's cancer, and never tells them it did not. It organizes evidence and states
  uncertainty honestly.
- The platform equally resists two failure modes: **prematurely alarming** the community,
  and **prematurely dismissing** a pattern that genuinely warrants investigation.

## 8. Legal and lawful-collection rules

Respect robots.txt, rate limits, terms of service, paywalls, and authentication. Do not
bypass access controls or CAPTCHAs. Observe copyright quotation limits (short, attributed
quotes; summaries rather than reproductions).
