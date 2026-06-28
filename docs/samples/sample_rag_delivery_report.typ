#set page(margin: 42pt)
#set text(font: "Arial", size: 10pt)
#set heading(numbering: none)

#let accent = rgb("#1457d9")
#let good = rgb("#11845b")
#let muted = rgb("#667085")
#let panel = rgb("#f6f8fb")

#let stat(label, value, color: accent) = block[
  #rect(fill: panel, radius: 5pt, inset: 10pt, width: 100%)[
    #text(size: 8pt, fill: muted, weight: "bold")[#upper(label)]
    #linebreak()
    #text(size: 18pt, fill: color, weight: "bold")[#value]
  ]
]

= RAG Chatbot Delivery Report

#text(fill: muted)[
  Sample handoff report for a document chatbot. The system retrieves relevant
  chunks and answers with visible source context.
]

#grid(columns: (1fr, 1fr, 1fr, 1fr), gutter: 8pt)[
  #stat("Documents", "1")
][
  #stat("Chunks", "8")
][
  #stat("Retriever", "TF-IDF")
][
  #stat("API", "FastAPI", color: good)
]

== Test Questions

#table(
  columns: (1.4fr, 1fr, 1.8fr),
  inset: 5pt,
  stroke: rgb("#d0d5dd"),
  [*Question*], [*Top Source*], [*Returned Context*],
  [Refund policy?], [company_policy.txt], [Returns are handled through the support policy section.],
  [Support response time?], [company_policy.txt], [The answer includes the matching support-policy chunk.],
  [Escalation path?], [company_policy.txt], [The answer cites the relevant operations section.],
)

== Delivered Files

- Document loader for `.txt` and `.pdf`
- Local vector store with chunk metadata
- CLI commands for ingest and chat
- FastAPI `/ask` and `/health` endpoints
- Tests that run without external API calls

== Scope Notes

- This template retrieves evidence; it does not promise perfect answers.
- Production deployments should add authentication, refresh jobs, monitoring, and a hosted vector database when needed.
