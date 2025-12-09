# Requirements Database Schema

**Location:** `./tmp/reqs.sqlite`

**Purpose:** Track $REQ_ID definitions and references across requirements, tests, and code

---

## Tables

### req_definitions

Stores requirement definitions from `./reqs/*.md`

| Column | Type | Description |
|--------|------|-------------|
| req_id | TEXT | Primary key, e.g., `$REQ_BUILD_001` |
| req_text | TEXT | Requirement title (after the colon on definition line) |
| source_attribution | TEXT | Source citation from `**Source:**` line, e.g., `./specs/FILE.md (Section: "Name")` |
| flow_file | TEXT | Path to requirements file, e.g., `./reqs/01_build.md` |

**Note:** In the case of duplicate $REQ_IDs (which is a defect), only the first occurrence of a $REQ_ID is stored as the definition

### req_locations

Stores all occurrences of $REQ_IDs across all files

| Column | Type | Description |
|--------|------|-------------|
| req_id | TEXT | The requirement ID |
| filespec | TEXT | File path where $REQ_ID appears |
| line_num | INTEGER | Line number in file |
| category | TEXT | File category: `reqs`, `tests`, or `code` |

**Index:** `idx_req_locations_id` on `req_id` for fast lookups

---

## Common Queries

**Find orphans** (in tests/code but not defined):
```sql
SELECT rl.req_id, rl.filespec, rl.line_num
FROM req_locations rl
WHERE rl.category IN ('tests', 'code')
  AND rl.req_id NOT IN (SELECT req_id FROM req_definitions)
```

**Find all locations for a $REQ_ID**:
```sql
SELECT filespec, line_num, category
FROM req_locations
WHERE req_id = '$REQ_BUILD_001'
ORDER BY category, filespec, line_num
```

---

## Maintenance

**Built by:** `build-req-index.py`

**Auto-rebuilt by:**
- `fix-duplicate-req-ids.py` (after fixing duplicates)
- `find-orphan-reqIDs.py` (before checking orphans)

**Used by:**
- `track-reqIDs.py` (show req + test + code for $REQ_IDs)
- `find-orphan-reqIDs.py` (detect undefined $REQ_IDs)
- Orchestration scripts during P3-P4 phases
