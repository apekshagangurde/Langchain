"""
PIIMiddleware
=============
Theory only — no code in this file.


WHAT IT IS
----------
`PIIMiddleware` is LangChain's ready-made deterministic guardrail for personally
identifiable information. It detects PII with regex detectors and then applies a
strategy to every match — redact, mask, hash, or block.

It is the guardrail you should reach for before writing your own patterns: the
detectors are already written, already tested, and already wired into the right
middleware hooks.


THE DETECTORS
-------------
Five types are built in:

    email           riya.sharma@example.com
    credit_card     4111 1111 1111 1111   (Luhn-validated, so fewer false hits)
    ip              192.168.1.42
    mac_address     00:1A:2B:3C:4D:5E
    url             https://internal.corp/x?t=1

Anything else you define yourself by passing a `detector` — either a regex string
or a function returning matches — with a name of your choosing ("api_key",
"aadhaar", "employee_id"). A custom type behaves exactly like a built-in one.


THE FOUR STRATEGIES
-------------------
This is the important choice. Each one trades information against safety.

1. REDACT  (the default)
   The value is replaced by a type label. Nothing survives.

       contact riya.sharma@example.com   ->   contact [REDACTED_EMAIL]
       card 4111 1111 1111 1111          ->   card [REDACTED_CREDIT_CARD]
       server 192.168.1.42               ->   server [REDACTED_IP]

   The model still learns that an email WAS mentioned — which is usually enough
   for it to reason ("I'll send it to the address you gave") — but it cannot
   read, repeat, or leak the value. Safest default for input.

2. MASK
   Part of the value survives, chosen so a human can recognise it without the
   secret being usable:

       riya.sharma@example.com   ->   riya.sharma@****.com
       4111 1111 1111 1111       ->   **** **** **** 1111
       192.168.1.42              ->   *.*.*.42
       00:1A:2B:3C:4D:5E         ->   **:**:**:**:**:5E
       https://internal.corp/x   ->   [MASKED_URL]

   Use masking when the user needs to CONFIRM which item is meant — "the card
   ending 1111" is exactly how a support conversation works. Note the trade-off:
   the last four digits are real, so masking leaks a little by design. A URL has
   no safely-partial form, so masking falls back to full replacement.

3. HASH
   The value is replaced by a stable fingerprint of itself:

       riya.sharma@example.com   ->   <email_hash:03ca3326>
       192.168.1.42              ->   <ip_hash:84b48121>

   The critical property: the SAME input always produces the SAME hash. So the
   model can still tell that two mentions are the same person, or that a value
   repeats across a long conversation, without ever seeing the value.

   That is what makes hash the right choice for correlation and analytics —
   counting distinct users, grouping events per IP, tracking a session — where
   redaction would collapse everything into one indistinguishable label.

   Caveat: a hash is pseudonymisation, not anonymisation. A small value space
   (an IP address, a phone number) can be brute-forced by hashing every
   candidate, so treat hashed PII as still sensitive.

4. BLOCK
   No transformation. The run stops with a `PIIDetectionError`.

   Use it when the presence of the value is itself the incident — an API key
   pasted into a chat, a password, a card number in a system that must never
   handle one. Blocking is the only strategy that gives you a hard guarantee;
   the other three still let the conversation continue.

Choosing between them, in one line each:
    redact  the model doesn't need the value
    mask    a human needs to recognise which value it is
    hash    something needs to correlate values without reading them
    block   the value must not be here at all


WHERE IT APPLIES — INPUT, OUTPUT, AND TOOL RESULTS
--------------------------------------------------
Three independent switches control WHERE the detector runs. This is the part
most people get wrong, because the defaults do not cover the leaks that matter
most.

  apply_to_input          default TRUE
      Scans user messages BEFORE the model call. This is the privacy boundary:
      redacted here, the value never reaches the model provider at all, so it
      never appears in their logs. If you care about data residency or vendor
      exposure, this is the switch that matters.

  apply_to_output         default FALSE
      Scans what the MODEL produced, before it reaches the user. Input scanning
      cannot help here — this text did not come from the user. It catches the
      model repeating something back, reconstructing a value, or reproducing PII
      it absorbed from a document. Turn it on whenever the model has access to
      records about real people.

  apply_to_tool_results   default FALSE
      Scans what TOOLS return, before the model sees it. This is the most
      commonly missed one and often the biggest leak: a database query, a CRM
      lookup, or a file read returns real customer data straight into the
      context, where it stays for the rest of the conversation and gets resent
      on every subsequent turn. A tool result is untrusted input from a privacy
      point of view, exactly like a user message.

Because the switches are independent, you can apply different treatment at
different points — mask a card on the way out so the user sees "ending 1111",
while redacting it on the way in so the model never holds it.


COMBINING RULES
---------------
Each `PIIMiddleware` instance handles ONE type with ONE strategy, so real
configurations stack several: block API keys, mask cards, hash IPs, redact
emails. They run in order, each pass over the text independent of the others.

Stacking is a feature, not clumsiness — it is what lets the policy be
per-type rather than one blunt setting for everything.


LIMITS — WHAT IT DOES NOT DO
----------------------------
  - it is regex-based, so it is deterministic and unbypassable, but literal:
    names, addresses, dates of birth and free-text medical details are NOT
    detected, because those have no reliable pattern
  - obfuscated values slip through ("riya dot sharma at example dot com")
  - false positives happen: a version string can look like an IP, an order
    number like a card
  - it protects the message content, not your database. If a tool can read
    every customer record, PII middleware only cleans what crosses the wire —
    the fix for an over-broad tool is a narrower tool
  - it is a boundary control, not compliance. GDPR/DPDP obligations concern
    storage, consent and retention, none of which a middleware addresses


HOW IT FITS THE BIGGER PICTURE
------------------------------
PIIMiddleware is the canonical DETERMINISTIC guardrail (file 2): fast, free,
testable, and immune to prompt injection. Pair it with a model-based judge
(file 3) for the things patterns cannot see — a user describing their own
medical history in prose contains no matchable PII pattern at all, yet is
exactly the content you may need to catch.


THE ONE-LINE VERSION
--------------------
PIIMiddleware finds the patterns you name and applies one of four fates —
redact, mask, hash, block — at any of three points: input, output, tool results.
"""
