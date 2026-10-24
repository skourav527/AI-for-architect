# Week 8 · Day 1 · Block 1 --- Evaluation Frame + Chunking Strategies

## Visual-First Revision Notes

> **Purpose:** A quick architecture reference for chunking strategies,
> context preservation, retrieval evaluation, metadata, and index
> lifecycle. Minimal theory; focus on diagrams, decisions, and practical
> examples.

------------------------------------------------------------------------

## 1. The Big Picture

``` mermaid
flowchart TD
    A["Source documents"] --> B["Parse and chunk"]
    B --> C["Attach metadata"]
    C --> D["Embed and index"]
    D --> E["Retrieve top K chunks"]
    E --> F["Authorize and rank"]
    F --> G["Assemble context"]
    G --> H["LLM answer + citations"]
    H --> I["Evaluate quality"]
    I -->|"Tune chunking / retrieval"| B
```

**Remember:** Chunking determines what can be retrieved. Ranking
determines where retrieved candidates appear. Generation determines how
the model uses the supplied context.

------------------------------------------------------------------------

## 2. Chunking Strategies --- Memory Map

``` mermaid
flowchart TD
    A["How should I split the document?"] --> B["Fixed-size"]
    A --> C["Recursive"]
    A --> D["Semantic"]
    A --> E["Structure-aware"]
    A --> F["Parent-child retrieval"]

    B --> B1["Split every N tokens"]
    B1 --> B2["Uniform / unstructured text; quick baseline"]

    C --> C1["Try paragraph → line → sentence separators"]
    C1 --> C2["General prose and Markdown"]

    D --> D1["Split when topic similarity drops"]
    D1 --> D2["Long documents with topic shifts"]

    E --> E1["Split by headings, clauses, functions, table structure"]
    E1 --> E2["Technical docs, APIs, contracts, structured content"]

    F --> F1["Retrieve small child chunk"]
    F1 --> F2["Expand to parent section for context"]
```

### Quick comparison

  ------------------------------------------------------------------------------
  Strategy              How it works      Good starting     Main risk /
                                          point for         trade-off
  --------------------- ----------------- ----------------- --------------------
  **Fixed-size**        Split every N     Quick baseline;   Can cut sentences,
                        tokens or         uniform or        tables, code, or
                        characters, often unstructured text related ideas
                        with overlap                        

  **Recursive**         Try separators in General prose,    Separator list may
                        order,            documents,        need tuning
                        e.g. paragraph →  Markdown          
                        line → sentence →                   
                        word                                

  **Semantic**          Split where       Long-form content Extra embedding pass
                        similarity        with meaningful   and threshold tuning
                        between adjacent  topic changes     
                        content drops                       

  **Structure-aware**   Parse headings,   Technical docs,   Requires suitable
                        lists, table      API references,   parsers and
                        rows, code        contracts,        structure-specific
                        blocks, clauses,  spreadsheets      logic
                        or other native                     
                        structure                           

  **Parent-child        Index smaller     Precise matching  Needs stable
  retrieval**           child chunks;     while preserving  `parent_id`; parent
                        retrieve a child, broader context   context uses token
                        then expand to                      budget
                        its parent                          
  ------------------------------------------------------------------------------

### Rules of thumb

-   **Fixed-size:** useful as a quick baseline, especially for a small
    corpus.
-   **Recursive:** a reasonable default for general prose unless the
    content has meaningful native structure.
-   **Semantic:** consider it when topic shifts inside long documents
    matter.
-   **Structure-aware:** prefer it when the document's structure carries
    meaning.
-   **Parent-child:** a retrieval/context pattern that can complement
    the strategies above.
-   These are starting hypotheses, not universal winners. Evaluate them
    on the same query set.

------------------------------------------------------------------------

## 3. Three Practical Choices

  -----------------------------------------------------------------------
  Document / question     Starting strategy       Preserve
  ----------------------- ----------------------- -----------------------
  Release changelog:      Structure-aware, or     Version heading +
  "Which version          recursive as a baseline date + change entries
  introduced this                                 
  change?"                                        

  Legal contract: "What   Structure-aware         Clause number + clause
  termination conditions                          text + qualifications;
  apply?"                                         retrieve referenced
                                                  exceptions when needed

  Codebase docstrings:    Structure-aware         Function/class
  "What does this                                 signature + docstring +
  function accept and                             parameters and relevant
  return?"                                        context
  -----------------------------------------------------------------------

### Example: changelog

A chunk containing only "Added retry support" may not answer "Which
version introduced retry support?" if the version heading was lost.
Preserve the version/date relationship in the chunk content or its
usable context.

### Example: legal contract

If Section 7 refers to an exception in Section 9, retrieving only the
sentence from Section 7 may omit a condition needed to answer correctly.
Retrieve the relevant clause and expand to its parent section or
referenced exception as required. Do not automatically send the entire
contract if targeted context is enough.

### Example: codebase documentation

Keep the function or class signature connected to its docstring,
parameters, return value, and relevant surrounding structure. A detached
docstring may not identify what it describes.

------------------------------------------------------------------------

## 4. Chunk Size and Overlap

``` mermaid
flowchart LR
    A["Too small"] --> A1["Precise fragment, but context may be missing"]
    B["Balanced"] --> B1["Relevant content with enough meaning"]
    C["Too large"] --> C1["Irrelevant content dilutes relevance; more context tokens"]
```

-   **Chunk size too small:** context or relationships may be lost.
-   **Chunk size too large:** embeddings can be diluted by unrelated
    material, and more context tokens are consumed.
-   **Overlap:** repeats some boundary content to reduce fragmentation.
-   **Too much overlap:** adds duplication and can increase index size
    and repeated retrieval.

> A 10--20% overlap is a heuristic from the reference notes, not a
> universal optimum. Tune chunk size and overlap with an evaluation set.

------------------------------------------------------------------------

## 5. Metadata Memory Map

``` mermaid
flowchart TD
    A["Chunk"] --> B["Identity"]
    A --> C["Context"]
    A --> D["Lifecycle"]
    A --> E["Security"]
    B --> B1["source_id · source_uri"]
    C --> C1["section / heading path · position · parent_id"]
    D --> D1["document_version · content hash · last_modified"]
    E --> E1["tenant · owner · classification"]
```

### Metadata checklist

  -----------------------------------------------------------------------
  Purpose                             Useful fields
  ----------------------------------- -----------------------------------
  Identity and citation               `source_id`, `source_uri`

  Context and expansion               `parent_id`, `position`,
                                      section/heading path

  Version and freshness               `document_version`, content hash,
                                      `last_modified`, `ingested_at`

  Security and ownership              tenant, owner, classification
  -----------------------------------------------------------------------

**Important distinction:** Metadata helps identify, filter, cite,
version, authorize, and expand chunks. Important meaning may also need
to remain in the chunk content itself---for example, a heading or
version label.

------------------------------------------------------------------------

## 6. Evaluation Metrics --- Which Problem Are You Measuring?

  -----------------------------------------------------------------------
  Question                            Metric / check
  ----------------------------------- -----------------------------------
  Did we retrieve the relevant        **Recall@K**
  document/chunk in the top K?        

  How many of the retrieved top K     **Precision@K**
  results are relevant?               

  How high is the first relevant      **MRR**
  result?                             

  How good is the overall ranking,    **nDCG**
  accounting for relevance grades?    

  Is the generated answer supported   Citation correctness / groundedness
  by its cited sources?               

  Is the system fast and affordable?  Latency / cost

  Is the requester allowed to access  **Authorization correctness ---
  the content?                        hard gate**
  -----------------------------------------------------------------------

### Retrieval evaluation loop

``` mermaid
flowchart TD
    A["Create labelled query set"] --> B["Run baseline retrieval"]
    B --> C["Measure Recall@K and ranking"]
    C --> D["Change chunking / metadata / retrieval"]
    D --> E["Run same queries again"]
    E --> F["Compare results"]
    F -->|"Improved?"| G["Keep change if quality and operational trade-offs justify it"]
    F -->|"Not improved"| D
```

-   Start with a practical set of roughly **20--50 labelled queries**
    for initial diagnosis. This is not necessarily statistically
    definitive.
-   Compare chunking configurations on the **same evaluation set**.
-   Recall@K is useful when the first concern is whether the relevant
    evidence enters the candidate set.
-   MRR and nDCG help evaluate ranking order.
-   A reranker cannot recover a relevant document that never entered the
    candidate pool.
-   Authorization is not a relevance metric: unauthorized content must
    not reach the model's usable context.

------------------------------------------------------------------------

## 7. Updates, Deletion, and Freshness

``` mermaid
flowchart TD
    A["Source changes or is deleted"] --> B["Identify affected source chunks"]
    B --> C["Replace, remove, or tombstone obsolete entries"]
    C --> D["Update vector index and parent relationships"]
    D --> E["Invalidate relevant caches / derived results"]
    E --> F["Verify propagation and access controls"]
    F --> G["Confirm freshness / deletion status"]
```

### Operational checklist

-   Use deterministic chunk IDs where appropriate so updates can replace
    old entries reliably.
-   Replace stale chunks when a source changes; avoid leaving old and
    new versions competing.
-   For deletion, remove or invalidate affected chunks and vector-index
    entries.
-   Update or remove obsolete parent records and invalidate relevant
    cached or derived results.
-   Track deletion propagation delay and verify that stale or
    unauthorized content cannot be retrieved during the transition.
-   Version and freshness metadata help identify stale content.
-   Changing chunking or embedding configuration can require reindexing;
    account for its cost and rollout strategy.

**Key rule:** An index is a changing cache of the source corpus. Stale
content can become a correctness or security problem.

------------------------------------------------------------------------

## 8. Architecture Decision Cheat Sheet

  -----------------------------------------------------------------------
  If the content/query has...         Start by considering...
  ----------------------------------- -----------------------------------
  Uniform, unstructured text and you  Fixed-size
  need a baseline                     

  Ordinary prose or Markdown          Recursive

  Strong topic shifts within long     Semantic
  text                                

  Headings, clauses, code, tables,    Structure-aware
  version relationships               

  A precise match that needs broader  Parent-child expansion
  context to answer safely            

  Exact IDs plus natural-language     Evaluate keyword, dense, and hybrid
  paraphrases                         retrieval on the same query set
  -----------------------------------------------------------------------

Do not assume hybrid retrieval always wins. Test keyword-only,
dense-only, and hybrid retrieval on the same labelled queries.

------------------------------------------------------------------------

## 9. Block 1 Active-Recall Checklist

Try to answer these from memory before moving on:

-   [ ] Explain the difference between fixed-size, recursive, semantic,
    and structure-aware chunking.
-   [ ] Choose a starting strategy for a changelog, legal contract, and
    codebase docstring---and explain why.
-   [ ] Explain why heading paths, version labels, clause numbers, and
    function signatures may need to stay connected to content.
-   [ ] Explain how chunk size and overlap can help or hurt retrieval.
-   [ ] Name useful metadata for identity, parent-child context,
    versioning, freshness, and authorization.
-   [ ] Distinguish Recall@K, Precision@K, MRR, and nDCG.
-   [ ] Explain why a reranker cannot recover evidence missing from the
    candidate pool.
-   [ ] Describe how source updates and deletion must propagate through
    chunks, indexes, parent records, and caches.
-   [ ] Explain why authorization must be enforced before content is
    sent to the model.

### Completion gate

Block 1 can be marked complete when you can explain the decision rules
above, update the `When to use each` column in
`chunking-strategies-comparison.md` in your own words, and confirm the
assigned reading/resources are complete. Do not mark reading or file
edits complete until you have actually done them.

------------------------------------------------------------------------

## 10. One-Minute Memory Map

``` text
CHUNKING
├── Fixed-size      → simple baseline
├── Recursive       → general prose
├── Semantic        → topic changes
├── Structure-aware → native document structure
└── Parent-child    → retrieve small, expand context

QUALITY
├── Recall@K        → relevant evidence found?
├── Precision@K     → retrieved results relevant?
├── MRR / nDCG      → ranking quality?
├── Groundedness    → answer supported?
└── Latency / cost  → operational trade-offs

PRODUCTION
├── Metadata        → identity, context, version, security
├── Freshness       → replace stale content
├── Deletion        → remove/invalidate all relevant copies
└── Authorization   → hard gate before model context
```
