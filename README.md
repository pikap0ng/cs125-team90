## 0 Clean start (reproducibility)

```bash
rm -f data/tmp_study_live.db
```
---

## 1 Run ingestion (multi-source pipeline)

```bash
python scripts/runIngestion.py \
  --providers uci,osm,google \
  --maxResults 20 \
  --sqlitePath data/tmp_study_live.db \
  --verbose
```

**Talk track:**
“Each provider fetches independently, then everything is normalized and merged into canonical rows.”

**What this shows:**
- provider modularity and fetch diagnostics
- merged output summary (`totalSourceRecords`, `totalCanonicalSpots`)

---

## 2 Verify pipeline output exists

### 2.1 Check tables

```bash
sqlite3 data/tmp_study_live.db ".tables"
```

**What this shows:** Expected persistence layer is present.

### 2.2 Compare source vs canonical counts

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT
   (SELECT COUNT(*) FROM sourceRecords) AS sourceRows,
   (SELECT COUNT(*) FROM canonicalSpots) AS canonicalRows;"
```

**What this shows:** canonical rows are the “items being ranked” and are often fewer than raw source rows.

### 2.3 Confirm provider contribution

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT provider, COUNT(*) AS n
 FROM sourceRecords
 GROUP BY provider
 ORDER BY n DESC;"
```

**What this shows:** multi-source ingestion is real, not simulated.

---

## 3 Show canonical representation + explainability fields

### 3.1 Canonical schema in action

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT name, latitude, longitude, address, onCampus
 FROM canonicalSpots
 LIMIT 10;"
```

**What this shows:** normalized spot representation across providers.

### 3.2 Features available for contextual ranking

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT name, features
 FROM canonicalSpots
 LIMIT 5;"
```

**What this shows:** ranking signals are materialized and queryable.

### 3.3 Provenance + confidence for trust/explainability

```bash
sqlite3 data/tmp_study_live.db ".mode line" \
"SELECT name, sourceIds, featureProvenance, confidence
 FROM canonicalSpots
 LIMIT 2;"
```

**What this shows:** every result can be explained by source and confidence metadata.

---

## 4 Four end-to-end functionality examples

## Example 1 — Off-campus café discovery (intent filter)

### 1A Find café-like places

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT name, address, features
 FROM canonicalSpots
 WHERE onCampus = 0
   AND (
     name LIKE '%Cafe%'
     OR name LIKE '%Coffee%'
     OR name LIKE '%Tea%'
     OR name LIKE '%Bakery%'
   )
 LIMIT 10;"
```

**Talk track:**
“This is an intent query: off-campus + café-like venues.”

### 1B Re-rank cafés for drivers (parking-first)

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT name, address, features
 FROM canonicalSpots
 WHERE onCampus = 0
   AND (
     name LIKE '%Cafe%'
     OR name LIKE '%Coffee%'
     OR name LIKE '%Tea%'
     OR name LIKE '%Bakery%'
   )
 ORDER BY (features LIKE '%parking%') DESC,
          name ASC
 LIMIT 5;"
```

**Talk track:**
“Same candidates, different ranking objective for a commuting-by-car user.”

### 1C Show source attribution for those results

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT name, sourceIds
 FROM canonicalSpots
 WHERE onCampus = 0
   AND (
     name LIKE '%Cafe%'
     OR name LIKE '%Coffee%'
     OR name LIKE '%Tea%'
     OR name LIKE '%Bakery%'
   )
 LIMIT 5;"
```

**What this example proves:** intent filtering, contextual ranking, and explainability.

---

## Example 2 — On-campus study spaces (campus context)

### 2A Restrict to on-campus spots

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT name, address, features
 FROM canonicalSpots
 WHERE onCampus = 1
 LIMIT 10;"
```

### 2B Rank for study convenience (WiFi + transport + parking)

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT name, onCampus, features
 FROM canonicalSpots
 WHERE onCampus = 1
 ORDER BY (features LIKE '%WiFi%') DESC,
          (features LIKE '%transit%') DESC,
          (features LIKE '%shuttle%') DESC,
          (features LIKE '%parking%') DESC
 LIMIT 5;"
```

### 2C Pull explainability details for one top result

```bash
sqlite3 data/tmp_study_live.db ".mode line" \
"SELECT name, features, featureProvenance, confidence
 FROM canonicalSpots
 WHERE onCampus = 1
 LIMIT 1;"
```

**What this example proves:** campus-aware retrieval and interpretable ranking using available features.

---

## Example 3 — Replace “open now” with intent pivot: cafés vs libraries

This directly demonstrates changing **search intent** (not time) while using the same unified dataset.

### 3A Café/coffee intent

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT name, address
 FROM canonicalSpots
 WHERE name LIKE '%Cafe%'
    OR name LIKE '%Coffee%'
    OR name LIKE '%Tea%'
 ORDER BY onCampus ASC, name ASC
 LIMIT 8;"
```

### 3B Library/study-resource intent

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT name, address
 FROM canonicalSpots
 WHERE name LIKE '%Library%'
    OR name LIKE '%Study%'
    OR name LIKE '%Learning%'
 ORDER BY onCampus DESC, name ASC
 LIMIT 8;"
```

### 3C Quantify distribution of both intents

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT
   SUM(CASE WHEN name LIKE '%Cafe%' OR name LIKE '%Coffee%' OR name LIKE '%Tea%' THEN 1 ELSE 0 END) AS cafeLike,
   SUM(CASE WHEN name LIKE '%Library%' OR name LIKE '%Study%' OR name LIKE '%Learning%' THEN 1 ELSE 0 END) AS libraryLike
 FROM canonicalSpots;"
```

**What this example proves:** same infrastructure supports multiple user intents and query modes.

---

## Example 4 — Same candidates, different user context (driver vs transit)

### 4A Driver profile (parking prioritized)

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT name, address, features
 FROM canonicalSpots
 WHERE onCampus = 0
 ORDER BY (features LIKE '%parking%') DESC,
          name ASC
 LIMIT 5;"
```

### 4B Transit/walker profile (transport notes prioritized)

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT name, address, features
 FROM canonicalSpots
 WHERE onCampus = 0
 ORDER BY (features LIKE '%transit%') DESC,
          (features LIKE '%transport%') DESC,
          (features LIKE '%shuttle%') DESC,
          name ASC
 LIMIT 5;"
```

**Talk track:**
“We are reranking the same candidate pool with different context weights.”

**What this example proves:** context alters ranking outcome.

---

## 5 demonstrate dedup/canonical keys explicitly

```bash
sqlite3 -header -column data/tmp_study_live.db \
"SELECT canonicalId, canonicalKey, name, sourceIds
 FROM canonicalSpots
 LIMIT 10;"
```

**What this shows:** each canonical row has a stable key and aggregated source identity metadata.

---

## 6 30-second closing summary for demo video

> “We ingest from UCI, OSM, and Google into one canonical representation. We can filter and rank by context such as on-campus status, parking, wifi, and transport notes. We can also pivot intent (cafés vs libraries) and rerank based on user profile (driver vs transit). Every result is explainable through source IDs, feature provenance, and confidence metadata.”