"""
Guardrail Techniques — Where To Put The Check
=============================================
Theory only — no code in this file.

Files 2-4 covered WHAT a guardrail decides (rules vs judge vs PII patterns).
This file covers WHERE it runs, because the same rule costs different amounts
and catches different things depending on the hook you attach it to.

Four techniques, cheapest first:

    1. before_agent hook        block before any LLM call        ZERO cost
    2. human in the loop        pause before a sensitive tool    human decides
    3. after_agent hook         validate the final answer        one call spent
    4. layered guardrails       all of the above, in order       defence in depth


=============================================================================
TECHNIQUE 1 — THE before_agent HOOK  (zero-cost blocking)
=============================================================================
`before_agent` runs ONCE, at the very start of the run, before the agent loop
begins — so before any model call, any tool call, any token spent.

    START -> [before_agent] -> before_model -> MODEL -> ... -> after_agent -> END

WHY THIS IS THE CHEAPEST GUARDRAIL THERE IS
    If the request is going to be refused anyway, refusing it here costs
    NOTHING. No prompt is sent, no tokens are billed, no latency is added
    beyond a regex match. A deny-list check at `before_agent` on a request that
    was always going to be blocked is free; the same check at `after_model`
    costs a full model call to reach the same verdict.

HOW IT BLOCKS
    The hook returns a state update containing a replacement message plus
    `jump_to: "end"`, which skips the entire loop and returns that message as
    the answer. The decorator must declare `can_jump_to=["end"]` so the graph
    builds that edge — otherwise the jump has nowhere to go.

WHAT BELONGS HERE
    - deny-list and allow-list topic checks
    - input length caps (reject a 500k-character paste before it is tokenised)
    - authentication and entitlement checks — is this user allowed to ask at all
    - rate limiting and quota checks
    - anything decidable from the user's message alone

before_agent VS before_model — THE DISTINCTION THAT MATTERS
    before_agent   runs ONCE per run.   Use for checks on the ORIGINAL request.
    before_model   runs before EVERY model call, including every loop iteration
                   after a tool returns. Use for checks that must re-run as the
                   conversation grows — trimming history, re-scanning tool
                   output that has entered the messages, per-call PII redaction.

    Putting a per-call check in before_agent means it runs once and then never
    again while the agent loops. Putting a one-time check in before_model means
    paying for it on every iteration. Neither is fatal, both are waste.


=============================================================================
TECHNIQUE 2 — HUMAN IN THE LOOP  (pause before a sensitive tool)
=============================================================================
Some actions cannot be un-done by an apology: sending an email, issuing a
refund, deleting a file, placing an order. For these, no automated guardrail is
trustworthy enough. The technique is to STOP and ask a person.

`HumanInTheLoopMiddleware` pauses the agent immediately before a listed tool
executes, surfaces the pending call, and waits.

    MODEL decides to call send_email
        -> guardrail sees send_email is on the list
        -> agent PAUSES, the tool has NOT run
        -> a human reviews the exact tool name and arguments
        -> a decision comes back
        -> agent RESUMES from precisely where it stopped

WHICH TOOLS PAUSE
    Configured per tool: pause on this one, auto-approve that one. Tools not
    mentioned at all run freely. So the pause is targeted — the agent still
    reads, searches and calculates at full speed, and only stops at the door of
    something irreversible.

THE FOUR DECISIONS A HUMAN CAN SEND
    APPROVE   run the tool exactly as the model proposed
    REJECT    do not run it; the model is told it was refused and why, and
              carries on with that knowledge — the run does not die
    EDIT      fix the arguments and then run it (wrong recipient, wrong amount)
    RESPOND   skip the tool entirely; the human supplies the result themselves,
              as though the tool had returned it

    REJECT and RESPOND are the two people underestimate. Rejecting is not an
    error: the refusal becomes a message the model can reason about. Responding
    lets a human short-circuit a tool that is broken or too slow.

THREADS AND CHECKPOINTS — WHY BOTH ARE REQUIRED
    A pause is only possible if the half-finished run can be put down and picked
    up later. That needs two things, and it fails without either:

    CHECKPOINTER — WHERE the paused run is saved.
        At the pause, the agent's entire state (messages so far, which tool is
        pending, its arguments) is written to the checkpointer. The Python call
        returns; nothing is held in memory waiting. `InMemorySaver` is fine for
        learning; a real deployment uses a database-backed saver so the run
        survives a process restart, a deploy, or a human who approves tomorrow
        morning.

    THREAD ID — WHICH paused run to resume.
        Passed in the config as `configurable.thread_id`. A thread is one
        conversation: every checkpoint written under that id belongs to it.
        Resuming means invoking the agent again with the SAME thread_id and a
        resume command carrying the decisions. A different thread_id starts a
        different conversation and will not find the pending approval.

    Together they are what makes the pause durable rather than a blocking call.
    The gap between pause and approval can be milliseconds or a week, and the
    process can die in between — the state is in the checkpointer, not in a
    stack frame.

WHAT THE PAUSE ACTUALLY RETURNS
    The invocation does not return a final answer; it returns an interrupt
    describing the pending action — the tool name, the arguments, and which
    decisions are permitted. Your application renders that for the human. The
    approval UI is yours to build; the middleware only guarantees that nothing
    runs until a decision arrives.

DESIGN NOTES
    - pause on the smallest possible set of tools; a system that asks about
      everything gets click-through approval, which is worse than none
    - show the human the ARGUMENTS, not just the tool name — "send_email" is
      not reviewable, "send_email to all-staff@ with subject X" is
    - HITL is the last layer, not the first: use the cheap automated guardrails
      to reduce how often a human is interrupted


=============================================================================
TECHNIQUE 3 — THE after_agent HOOK  (validate the final response)
=============================================================================
`after_agent` runs ONCE, when the loop has finished and an answer exists, before
that answer is returned. It is the last thing between the agent and the user.

    ... -> MODEL -> after_model -> [after_agent] -> END -> user

WHAT IT IS FOR
    Judging the FINISHED answer as a whole. Only here does the complete response
    exist — after_model sees each intermediate reply, including ones that are
    just tool calls, and cannot judge a conclusion that has not been reached yet.

    - is the final answer supported by the sources that were retrieved
    - does it leak a system prompt, internal code name, or credential
    - does it give advice the assistant is not permitted to give
    - is the format right for whatever consumes it next
    - is the tone acceptable

REPLACE OR MUTATE — THE TWO WAYS TO FIX IT
    A guardrail here rarely wants to block: the work is already done and paid
    for. Usually it edits.

    MUTATE   keep the answer, change the offending part — mask the card number,
             strip the internal URL, cut the paragraph that overstepped, append
             a disclaimer. The user still gets a useful reply, which is the
             whole reason to prefer mutation.

    REPLACE  discard the answer and substitute a fixed safe message. Reserved
             for a response so wrong that no edit rescues it — a leaked secret,
             a serious policy breach.

    Mechanically both work the same way: return the message with the SAME id as
    the original, and it overwrites it in state rather than appending a second
    reply. A new id would leave the unsafe text sitting in the history right
    above your correction.

THE COST NOTE
    Everything caught here was already paid for in full — the model calls, the
    tool calls, the latency. That is the argument for pushing checks as early as
    they will go. But some things are only knowable at the end, and for those,
    paying is correct.


=============================================================================
TECHNIQUE 4 — LAYERED GUARDRAILS
=============================================================================
No single hook is sufficient, because each one is blind to what the others see.
Production systems layer them, cheapest and most certain first:

    LAYER 1   before_agent, deterministic
              deny lists, length caps, auth, quota
              cost: zero. Filters the obvious before a token is spent.

    LAYER 2   before_model, deterministic
              PII redaction on input and on tool results, history trimming
              cost: near zero. Runs every iteration, so it catches PII that
              entered the conversation from a tool halfway through.

    LAYER 3   before_model or after_model, model-based
              an LLM judge on intent, injection, topicality
              cost: a model call per request. Only reached by what survived
              layers 1-2, so you pay for it far less often.

    LAYER 4   wrap_tool_call, deterministic
              path restrictions, amount caps, argument sanitising
              cost: zero, and this is the layer that prevents real damage,
              because it guards ACTIONS rather than words.

    LAYER 5   human in the loop
              approval on the small set of genuinely irreversible tools
              cost: human attention — the most expensive resource in the stack,
              so spend it last and rarely.

    LAYER 6   after_agent
              final validation, groundedness, leak check, mutate or replace
              cost: already spent. The safety net for what everything above
              missed.

WHY THE ORDERING IS THE POINT
    Each layer reduces the volume reaching the next. Cheap-and-certain filters
    protect expensive-and-fallible ones, and the layer that cannot be argued
    with (code) wraps the layer that can (a judge model, a tired human).

DEFENCE IN DEPTH, NOT DUPLICATION
    Layers should catch DIFFERENT failures, not the same one repeatedly. Three
    checks for banned keywords is one guardrail written three times. A keyword
    check, an intent judge, and a tool-argument cap are three genuinely
    different failures covered.

THE FAILURE MODE TO AVOID
    Over-guarding. Every layer adds latency, cost, and false positives, and a
    system that refuses too much gets switched off — which leaves you with no
    guardrails at all. Start with layers 1 and 4 (both free, both effective),
    add 5 for anything irreversible, and only add the model-based layers when a
    real failure justifies the spend.


THE ONE-LINE VERSION
--------------------
Block it free at before_agent, guard the actions at the tool call, ask a human
before anything irreversible, and check the finished answer at after_agent —
in that order, because each layer makes the next one cheaper.
"""
