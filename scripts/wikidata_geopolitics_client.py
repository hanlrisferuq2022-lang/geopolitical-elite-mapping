"""
Wikidata SPARQL Client for Geopolitical Elite Mapping

Queries Wikidata for political entities, organizations, treaties,
and political figures. Used by the geopolitical-elite-mapping skill
to establish structured information about geopolitical actors.

API: https://query.wikidata.org/sparql (free, no auth required)
"""

import requests
import hashlib
import json
import logging
import time
from collections import OrderedDict
from typing import Optional

logger = logging.getLogger(__name__)

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "GeopoliticalMapping-Skill/1.0.0 (geopolitical-elite-mapping; research)"
REQUEST_DELAY = 1.0  # seconds between requests (polite rate limiting)
MAX_RETRIES = 3      # exponential backoff retries for transient failures
CACHE_MAX_SIZE = 200 # max cached queries

_last_request_time = 0.0
_cache: OrderedDict[str, list[dict]] = OrderedDict()


def _escape_sparql(s: str) -> str:
    """Escape special chars for SPARQL string literals."""
    return (s.replace('\\', '\\\\')
             .replace('"', '\\"')
             .replace("'", "\\'")
             .replace('\n', '\\n')
             .replace('\r', '\\r')
             .replace('\t', '\\t'))


def _cache_key(query: str) -> str:
    """Generate a compact hash key for a SPARQL query string."""
    return hashlib.sha256(query.strip().encode()).hexdigest()


def _cache_put(key: str, value: list[dict]) -> None:
    """Insert into LRU-style cache with size limit."""
    global _cache
    _cache[key] = value
    while len(_cache) > CACHE_MAX_SIZE:
        _cache.popitem(last=False)


def _sparql_query(query: str, use_cache: bool = True) -> list[dict]:
    """Execute a SPARQL query against Wikidata and return bindings.

    Features:
    - Rate limiting (1 req/s)
    - Exponential backoff retry (3 attempts) for 429/503/timeout
    - In-memory LRU cache (max 200 entries)
    """
    global _last_request_time

    key = _cache_key(query)
    if use_cache and key in _cache:
        return _cache[key]

    for attempt in range(MAX_RETRIES):
        elapsed = time.time() - _last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)

        try:
            r = requests.get(
                WIKIDATA_SPARQL_ENDPOINT,
                params={"query": query, "format": "json"},
                headers={"User-Agent": USER_AGENT},
                timeout=30,
            )
            _last_request_time = time.time()

            if r.status_code == 200:
                data = r.json()
                results = data.get("results", {}).get("bindings", [])
                if use_cache:
                    _cache_put(key, results)
                return results

            if r.status_code in (429, 503) and attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                logger.warning(
                    "HTTP %d, retrying in %ds (attempt %d/%d)",
                    r.status_code, wait, attempt + 1, MAX_RETRIES,
                )
                time.sleep(wait)
                continue

            logger.error("SPARQL query failed: HTTP %d", r.status_code)
            return []

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                logger.warning(
                    "Timeout, retrying in %ds (attempt %d/%d)",
                    wait, attempt + 1, MAX_RETRIES,
                )
                time.sleep(wait)
                continue
            logger.error("SPARQL query timeout after all retries")
            return []

        except Exception as e:
            logger.error("SPARQL query error: %s", e)
            return []

    return []


def _extract_label(binding: dict, key: str) -> str:
    """Extract a label value from a SPARQL binding."""
    return binding.get(key, {}).get("value", "")


def _extract_id(binding: dict, key: str) -> str:
    """Extract a Wikidata QID from a SPARQL binding URI."""
    uri = binding.get(key, {}).get("value", "")
    if "/entity/" in uri:
        return uri.split("/entity/")[-1]
    return uri


# ============================================================
# Political Organization Queries
# ============================================================

def query_political_organization(org_name: str) -> Optional[dict]:
    """
    Query Wikidata for a political organization's basic info.
    Searches for political parties, military alliances, international orgs, etc.

    Args:
        org_name: Name of the organization (e.g., "NATO", "OPEC", "上海合作组织")

    Returns:
        Dict with: qid, name, description, inception, member_count, headquarters
        None if not found.
    """
    safe_name = _escape_sparql(org_name)

    # Search both English and Chinese labels
    query = f'''
    SELECT ?org ?orgLabel ?orgDescription ?inception ?hqLabel
           (COUNT(DISTINCT ?member) AS ?memberCount)
    WHERE {{
      {{ ?org rdfs:label "{safe_name}"@en . }}
      UNION
      {{ ?org rdfs:label "{safe_name}"@zh . }}
      ?org wdt:P31/wdt:P279* ?type .
      FILTER(?type IN (
        wd:Q484652,   # international organization
        wd:Q7210356,  # political organization
        wd:Q4120211,  # regional organization
        wd:Q1335818,  # military alliance
        wd:Q7278,     # political party
        wd:Q45382,    # cartel
        wd:Q163740    # nonprofit organization
      ))
      OPTIONAL {{ ?org wdt:P571 ?inception . }}
      OPTIONAL {{ ?org wdt:P159 ?hq . }}
      OPTIONAL {{ ?org wdt:P150|wdt:P527 ?member . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,zh,ar,ru,fr" }}
    }}
    GROUP BY ?org ?orgLabel ?orgDescription ?inception ?hqLabel
    LIMIT 5
    '''
    bindings = _sparql_query(query)
    if not bindings:
        return None

    b = bindings[0]
    inception_val = _extract_label(b, "inception")
    if inception_val and "T" in inception_val:
        inception_val = inception_val.split("T")[0]  # Extract date only

    return {
        "qid": _extract_id(b, "org"),
        "name": _extract_label(b, "orgLabel"),
        "description": _extract_label(b, "orgDescription"),
        "inception": inception_val,
        "headquarters": _extract_label(b, "hqLabel"),
        "member_count": int(_extract_label(b, "memberCount") or 0),
    }


def query_organization_members(org_name: str = None, org_qid: str = None) -> list[dict]:
    """
    Query Wikidata for members/member states of an organization.

    Args:
        org_name: Name of the organization
        org_qid: Wikidata QID (takes priority if provided)

    Returns:
        List of dicts with: member_name, member_qid
    """
    if org_qid:
        filter_clause = f"wd:{org_qid}"
    elif org_name:
        safe_name = _escape_sparql(org_name)
        find_query = f'''
        SELECT ?org WHERE {{
          {{ ?org rdfs:label "{safe_name}"@en . }}
          UNION
          {{ ?org rdfs:label "{safe_name}"@zh . }}
        }} LIMIT 1
        '''
        bindings = _sparql_query(find_query)
        if not bindings:
            return []
        filter_clause = f"wd:{_extract_id(bindings[0], 'org')}"
    else:
        return []

    query = f'''
    SELECT ?member ?memberLabel WHERE {{
      {filter_clause} wdt:P150|wdt:P527 ?member .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,zh" }}
    }}
    LIMIT 100
    '''
    bindings = _sparql_query(query)

    return [
        {
            "member_name": _extract_label(b, "memberLabel"),
            "member_qid": _extract_id(b, "member"),
        }
        for b in bindings
    ]


# ============================================================
# Political Figure Queries
# ============================================================

def query_political_figure(person_name: str, expected_role: str = None) -> Optional[dict]:
    """
    Query Wikidata for a political figure's info.

    Args:
        person_name: Full name (e.g., "Henry Kissinger", "习近平")
        expected_role: Optional role/position keyword for disambiguation

    Returns:
        Dict with: qid, name, description, positions, affiliations, nationality
    """
    safe_name = _escape_sparql(person_name)

    query1 = f'''
    SELECT ?person ?personLabel ?personDescription ?nationalityLabel WHERE {{
      {{ ?person rdfs:label "{safe_name}"@en . }}
      UNION
      {{ ?person rdfs:label "{safe_name}"@zh . }}
      ?person wdt:P31 wd:Q5 .
      OPTIONAL {{ ?person wdt:P27 ?nationality . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,zh,ar,ru,fr" }}
    }} LIMIT 5
    '''
    bindings1 = _sparql_query(query1)
    if not bindings1:
        return None

    # Disambiguation: pick best match
    best = bindings1[0]
    if expected_role and len(bindings1) > 1:
        role_lower = expected_role.lower()
        for candidate in bindings1:
            desc = _extract_label(candidate, "personDescription").lower()
            if role_lower in desc:
                best = candidate
                logger.info(
                    "Disambiguated '%s' → matched description containing '%s'",
                    person_name, expected_role,
                )
                break

    qid = _extract_id(best, "person")

    # Step 2: Get positions held and party affiliations
    query2 = f'''
    SELECT ?posLabel ?partyLabel ?startTime ?endTime WHERE {{
      OPTIONAL {{
        wd:{qid} p:P39 ?posStatement .
        ?posStatement ps:P39 ?pos .
        OPTIONAL {{ ?posStatement pq:P580 ?startTime . }}
        OPTIONAL {{ ?posStatement pq:P582 ?endTime . }}
      }}
      OPTIONAL {{ wd:{qid} wdt:P102 ?party . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,zh" }}
    }}
    LIMIT 30
    '''
    bindings2 = _sparql_query(query2)

    positions = []
    parties = set()
    for b2 in bindings2:
        pos = _extract_label(b2, "posLabel")
        party = _extract_label(b2, "partyLabel")
        start = _extract_label(b2, "startTime")
        end = _extract_label(b2, "endTime")
        if pos:
            start_year = start[:4] if start else "?"
            end_year = end[:4] if end else "present"
            positions.append(f"{pos} ({start_year}–{end_year})")
        if party:
            parties.add(party)

    return {
        "qid": qid,
        "name": _extract_label(best, "personLabel"),
        "description": _extract_label(best, "personDescription"),
        "nationality": _extract_label(best, "nationalityLabel"),
        "positions": "; ".join(dict.fromkeys(positions)),  # deduplicate, preserve order
        "parties": ", ".join(sorted(parties)),
    }


# ============================================================
# Treaty / Agreement Queries
# ============================================================

def query_treaty(treaty_name: str) -> Optional[dict]:
    """
    Query Wikidata for a treaty or international agreement.

    Args:
        treaty_name: Name of the treaty (e.g., "Treaty of Westphalia", "JCPOA")

    Returns:
        Dict with: qid, name, description, date_signed, signatories_count
    """
    safe_name = _escape_sparql(treaty_name)

    query = f'''
    SELECT ?treaty ?treatyLabel ?treatyDescription ?dateSigned
           (COUNT(DISTINCT ?signatory) AS ?signatoryCount)
    WHERE {{
      {{ ?treaty rdfs:label "{safe_name}"@en . }}
      UNION
      {{ ?treaty rdfs:label "{safe_name}"@zh . }}
      OPTIONAL {{ ?treaty wdt:P585 ?dateSigned . }}
      OPTIONAL {{ ?treaty wdt:P710 ?signatory . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,zh" }}
    }}
    GROUP BY ?treaty ?treatyLabel ?treatyDescription ?dateSigned
    LIMIT 5
    '''
    bindings = _sparql_query(query)
    if not bindings:
        return None

    b = bindings[0]
    date_val = _extract_label(b, "dateSigned")
    if date_val and "T" in date_val:
        date_val = date_val.split("T")[0]

    return {
        "qid": _extract_id(b, "treaty"),
        "name": _extract_label(b, "treatyLabel"),
        "description": _extract_label(b, "treatyDescription"),
        "date_signed": date_val,
        "signatories_count": int(_extract_label(b, "signatoryCount") or 0),
    }


# ============================================================
# Conflict / War Queries
# ============================================================

def query_conflict(conflict_name: str) -> Optional[dict]:
    """
    Query Wikidata for a military conflict or war.

    Args:
        conflict_name: Name of the conflict (e.g., "Gulf War", "叙利亚内战")

    Returns:
        Dict with: qid, name, description, start_date, end_date, participants
    """
    safe_name = _escape_sparql(conflict_name)

    query = f'''
    SELECT ?conflict ?conflictLabel ?conflictDescription
           ?startDate ?endDate
    WHERE {{
      {{ ?conflict rdfs:label "{safe_name}"@en . }}
      UNION
      {{ ?conflict rdfs:label "{safe_name}"@zh . }}
      ?conflict wdt:P31/wdt:P279* wd:Q180684 .  # instance of conflict
      OPTIONAL {{ ?conflict wdt:P580 ?startDate . }}
      OPTIONAL {{ ?conflict wdt:P582 ?endDate . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,zh,ar,ru,fr" }}
    }}
    LIMIT 5
    '''
    bindings = _sparql_query(query)
    if not bindings:
        return None

    b = bindings[0]
    qid = _extract_id(b, "conflict")

    # Get participants
    query2 = f'''
    SELECT ?participantLabel WHERE {{
      wd:{qid} wdt:P710 ?participant .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,zh" }}
    }}
    LIMIT 30
    '''
    bindings2 = _sparql_query(query2)
    participants = [_extract_label(b2, "participantLabel") for b2 in bindings2]

    start = _extract_label(b, "startDate")
    end = _extract_label(b, "endDate")

    return {
        "qid": qid,
        "name": _extract_label(b, "conflictLabel"),
        "description": _extract_label(b, "conflictDescription"),
        "start_date": start[:10] if start else "",
        "end_date": end[:10] if end else "",
        "participants": participants,
    }


# ============================================================
# Batch Query
# ============================================================

def batch_query_entities(names: list[str], entity_type: str = "organization") -> dict[str, Optional[dict]]:
    """
    Batch query multiple entities by name.

    Args:
        names: List of entity names
        entity_type: One of "organization", "person", "treaty", "conflict"

    Returns:
        Dict mapping each name to its query result.
    """
    query_fn = {
        "organization": query_political_organization,
        "person": query_political_figure,
        "treaty": query_treaty,
        "conflict": query_conflict,
    }.get(entity_type)

    if not query_fn:
        logger.error("Unknown entity_type: %s", entity_type)
        return {name: None for name in names}

    results = {}
    for name in names:
        results[name] = query_fn(name)

    return results


def clear_cache():
    """Clear the in-memory query cache."""
    global _cache
    _cache.clear()


# --- CLI usage ---
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="[wikidata-geo] %(levelname)s: %(message)s")

    if len(sys.argv) < 3:
        print("Usage:")
        print("  python wikidata_geopolitics_client.py --org <organization_name>")
        print("  python wikidata_geopolitics_client.py --person <person_name>")
        print("  python wikidata_geopolitics_client.py --treaty <treaty_name>")
        print("  python wikidata_geopolitics_client.py --conflict <conflict_name>")
        print("  python wikidata_geopolitics_client.py --members <organization_name>")
        sys.exit(1)

    mode = sys.argv[1]
    name = " ".join(sys.argv[2:])

    if mode == "--org":
        print(f"Querying organization: {name}")
        result = query_political_organization(name)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("  Not found in Wikidata")

    elif mode == "--person":
        print(f"Querying political figure: {name}")
        result = query_political_figure(name)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("  Not found in Wikidata")

    elif mode == "--treaty":
        print(f"Querying treaty: {name}")
        result = query_treaty(name)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("  Not found in Wikidata")

    elif mode == "--conflict":
        print(f"Querying conflict: {name}")
        result = query_conflict(name)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("  Not found in Wikidata")

    elif mode == "--members":
        print(f"Querying members of: {name}")
        members = query_organization_members(org_name=name)
        if members:
            print(f"Found {len(members)} members:")
            for m in members:
                print(f"  {m['member_name']} ({m['member_qid']})")
        else:
            print("  No members found in Wikidata")

    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
