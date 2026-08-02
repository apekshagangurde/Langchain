# Subgraph: a LangGraph graph that is itself compiled and then added as a
# node inside a parent graph, letting a self-contained workflow (with its
# own state and nodes) be reused and composed as a single step elsewhere.
#
# Why we need it:
#
# - Reusability: build a workflow once (e.g. a "research" graph) and
#   plug that same compiled graph into multiple parent graphs as a
#   node, instead of copy-pasting its nodes/edges into every parent
#   that needs the same behavior.
# - Modularity: each subgraph encapsulates its own nodes/edges/logic,
#   so the parent graph only has to know about one node, not every
#   internal step of that piece of work.
# - Isolated state: a subgraph can keep its own state schema, separate
#   from the parent's, with explicit input/output keys mapping between
#   the two — internal fields don't leak into the parent's state.
# - Independent testing: a subgraph can be invoked and debugged on its
#   own, before it's ever wired into a larger graph.
# - Team ownership: different people/teams can build and maintain a
#   subgraph independently, then hand over just the compiled graph.
# - Composability for multi-agent systems: complex graphs (e.g.
#   multi-agent setups) are easier to reason about as a small number
#   of subgraphs plugged together, rather than one giant flat graph.
#
# Types of subgraphs (by how they share state with the parent):
#
# - Shared schema: the subgraph's state has at least one key in common
#   with the parent's state. The compiled subgraph can be added
#   directly as a node — LangGraph passes the shared keys straight
#   through, no translation needed.
# - Different schema: the subgraph's state has no keys in common with
#   the parent's. A wrapper node function is added to the parent
#   instead of the compiled subgraph itself; that function transforms
#   the parent state into the subgraph's input, invokes the subgraph,
#   then transforms its output back into the parent's state.
