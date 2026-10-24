# [HER Hack-Astron # 7] [Open Source AI for Good] Rural Signal

## Project name and track

**Project name:** Rural Signal
**Track:** Disaster preparedness and response + accessibility

## Who this helps and what problem it solves

**Target users:** People in rural communities, especially households dealing
with fragmented information sources, imperfect connectivity, and basic-phone
access.

**Concrete scenario and problem:** A rural resident may receive a weather
warning, a county road notice, or a forwarded community report in different
formats and with different levels of reliability. Under time pressure, the
resident needs one clear next step without losing the difference between an
official notice and unverified chatter.

**Expected public benefit:** Rural Signal turns each notice into a plain-language
action card with visible source status, locked critical facts, bounded actions,
explicit unknowns, and a flip-phone-sized SMS preview.

## How Spark-X2.6-4B is used

**Model source and revision:** Official
`XHToken/Spark-X2.6-4B-GGUF`, Q4_K_M, revision
`fe31f8d64890302cc3a1d365d700357b4b75ba77`, SHA-256
`91cb2811aebb47ac916aa619d27d4cdd7f4143106b7917accb8ead4cd7f5cbd9`.

**The model's role:** Spark writes the concise plain-language summary, selects
from case-specific approved actions and unknowns, and creates the SMS preview.
Ordinary Python code owns the incident, location, time, source, and trust status
and validates every model-authored field before display.

**Other models, tools, or services:** llama.cpp performs local CPU inference.
Agent J, using an OpenAI model, assisted with implementation, test design,
interface copy, and submission preparation. No hosted model is used when Rural
Signal runs.

## Demo — illustrated walkthrough

### 1. Official flash-flood notice

![Official flash-flood case](demo/01-official-flash-flood.jpg)

The synthetic National Weather Service notice identifies a flash-flood warning
at County Road 12 at Dry Creek. Rural Signal preserves the official status,
location, observation time, and validity time outside Spark. Spark turns the
notice into a concise summary, approved actions, one explicit unknown, and a
137-character SMS preview.

### 2. Adversarial unverified community report

![Adversarial unverified case](demo/02-adversarial-unverified.jpg)

The incoming source text contains a malicious instruction telling the model to
ignore its rules and call an unverified loose-cow report official and confirmed.
After a fresh local run, Rural Signal still displays `UNVERIFIED`, explicitly
says the report has not been officially confirmed, limits the actions to the
approved list, and produces a 107-character SMS preview. The validator passed
in 19.13 seconds and reported: “Trust boundary held. Nothing was sent.”

## How to reproduce

**Code repository or runnable example:**
https://github.com/foff4580-sys/rural-signal

**Setup and run:** Download the official Q4_K_M GGUF, provide
`RURAL_SIGNAL_LLAMA` and `RURAL_SIGNAL_MODEL`, then run
`python3 test_engine.py`, `python3 verify_package.py`,
`python3 engine.py --all`, and `python3 app.py`. Open
`http://127.0.0.1:8787/`.

**Runtime and versions:** Python 3.12.3; llama.cpp 0.7.0-dev build 11838,
commit `4231b23dc`.

**Hardware and quantization:** Linux x86-64; Intel Core Ultra 7 255H; CPU
inference with 8 threads; Spark-X2.6-4B Q4_K_M.

**Key inference settings:** 4096-token context, temperature 0, reasoning
disabled with budget 0, 320 output-token limit, single-turn mode. The full
prompt builder and deterministic validator are included in `engine.py`.

## Results and limitations

**Observed results:** Four of four fresh synthetic cases passed the final
validator in 18.64–20.04 seconds in the final release run. Six deterministic
unit tests cover locked-field mutation, invented time, unsupported action,
trust-status promotion, and SMS length. The illustrated adversarial run passed
in 19.13 seconds with its `UNVERIFIED` status intact.

**Limitations:** The sample is four synthetic English-language cases on one
computer. This is not evidence that every notice, model output, or attack will
be handled correctly. The prototype has no live data ingestion, telecom
gateway, or agency integration; it sends nothing. It is not an emergency
service and does not replace official alerts, emergency instructions,
professional review, or human judgment. Failed output is withheld.

## Contributors and disclosure

**Individual / team:** Individual entry by Jere.

**Contributor contributions:** Jere defined the target problem, product
boundary, and public-interest goal and authorized the final entry.

**AI-assisted development disclosure:** Agent J, an AI assistant using an
OpenAI model, assisted with research, implementation, interface copy, testing,
and submission preparation. Spark-X2.6-4B is the application model demonstrated
in the product. Agent J is not presented as a human participant.

**Data sources and authorization:** Every incident and location in the
demonstration is synthetic. No personal data, live emergency feed, private
notice, or third-party operational data is included.
