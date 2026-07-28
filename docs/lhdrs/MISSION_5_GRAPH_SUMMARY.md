# Mission 5 evidence graph summary

The normalized graph contains **1,229 nodes**, **1,614 edges**, and **27 relationship types**. All 18 first-edition edges are preserved. Mission 5 adds current address-based tract/neighborhood candidates, builder products, County permit and escrow snapshots, aggregate built-and-occupied counts, commercial status snapshots, and full-coverage 2005/2009/2010 imagery observations.

Every edge carries valid-time fields, evidence IDs, source IDs, confidence, version, review status, and limitations. Blank valid-time values mean the relationship is not temporally bounded; they are not interpreted as indefinite historical truth. Current crosswalk edges are not historical parentage or lifecycle edges.

The seven required example queries are stored in `data/development/graph_query_results.json`. Queries that require dated occupancy or active-construction geometry return `blocked`, not an empty factual answer.

![Graph summary](../../reports/assets/lhdrs_graph/graph_summary.png)
