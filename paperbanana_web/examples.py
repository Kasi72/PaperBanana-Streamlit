"""Compact examples for the public authoring workspace."""

EXAMPLE_METHOD = """## Retrieval-augmented generation pipeline

Documents are split into semantic chunks and encoded with an embedding model.
The embeddings and source metadata are stored in a vector index. At query time,
the user question is embedded and the top-k chunks are retrieved. A language
model receives the question and retrieved evidence, produces an answer, and
returns citations to the source chunks. An evaluator checks answer faithfulness
and sends low-confidence answers back through retrieval with an expanded query.
"""

EXAMPLE_CAPTION = (
    "Overview of the retrieval-augmented generation workflow, showing offline "
    "indexing, online retrieval and grounded answer generation, plus the "
    "faithfulness feedback loop."
)
