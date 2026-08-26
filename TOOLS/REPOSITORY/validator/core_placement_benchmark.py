#!/usr/bin/env python3
"""Placement-first benchmark: score canonical destination from identity, not scope trivia."""
from __future__ import annotations
import json
from pathlib import Path

CULTURE_ROOT = '03_PEOPLES/CULTURES/HEARTH'
REGIONS = {'PLAINS','MOUNTAINS','RIVER','WETLANDS','DESERT','COAST'}

def norm(p):
    return Path(p).as_posix().upper()

def expected(path):
    """Return the destination represented by the file's existing canonical path."""
    p = norm(path)
    if f'/{CULTURE_ROOT}/' in p:
        for r in REGIONS:
            if f'/{CULTURE_ROOT}/{r}/' in p:
                return f'{CULTURE_ROOT}/{r}'
        if f'/{CULTURE_ROOT}/COMPARATIVE/' in p:
            return f'{CULTURE_ROOT}/COMPARATIVE'
        return CULTURE_ROOT
    if '/07_ARCHIVE/HISTORICAL/' in p:
        return '07_ARCHIVE/HISTORICAL'
    return str(Path(path).parent)

def identity_destination(path, identity):
    """Map identity_layer to canonical destination.

    Placement is deliberately derived from identity_layer first. scope.region is
    only used to specialize REGIONAL_SPECIALIZATION; it is never treated as the
    destination by itself. This keeps a regional scope from hijacking a
    CANONICAL_ROOT or SUPPORTING_ARTIFACT placement.
    """
    identity = identity or {}
    layer = identity.get('identity_layer')
    scope = identity.get('scope') or {}
    role = identity.get('role')
    content = identity.get('content_type')
    region = scope.get('region')
    region = region.upper() if isinstance(region, str) else None
    if region not in REGIONS:
        region = None

    if layer == 'HISTORICAL_ARTIFACT' or role == 'HISTORICAL':
        return '07_ARCHIVE/HISTORICAL'
    if layer == 'SUPPORTING_ARTIFACT' or role == 'SUPPORTING':
        if content == 'CULTURE' or '/03_PEOPLES/CULTURES/' in norm(path):
            return f'{CULTURE_ROOT}/COMPARATIVE'
        return None
    if content == 'CULTURE':
        if layer == 'REGIONAL_SPECIALIZATION' and region:
            return f'{CULTURE_ROOT}/{region}'
        if layer == 'CANONICAL_ROOT':
            return CULTURE_ROOT
        # Legacy/unknown identity layers are not allowed to fall back to
        # scope.region; leave them for review rather than inventing placement.
        return None
    return None

def main():
    root = Path('TOOLS/REPOSITORY/REPORTS')
    tri = root / 'CORE_DOCUMENT_TRIAGE.json'
    data = json.loads(tri.read_text(encoding='utf-8')) if tri.exists() else {'cases': []}
    rows = []
    for c in data.get('cases', []):
        for side in ('a', 'b'):
            path = c.get('documents', {}).get(side, '')
            actual = c.get('placement', {}).get(side, {})
            identity = c.get('identity', {}).get(side, {})
            exp = expected(path)
            proposed = identity_destination(path, identity)
            # If identity does not yet support a safe destination, retain the
            # old parent only as an explicitly unscored review state.
            scored = proposed is not None
            rows.append({
                'relationship_id': c.get('relationship_id'),
                'document': path,
                'expected_parent': exp,
                'proposed_parent': proposed,
                'placement_correct': scored and proposed == exp,
                'placement_scored': scored,
                'identity_layer': identity.get('identity_layer'),
                'identity_scope': identity.get('scope', {}),
                'identity_role': identity.get('role'),
                'identity_content_type': identity.get('content_type'),
                'relationship_decision': c.get('decision'),
                'relationship_tags': c.get('layered_comparison', {}).get('relationship_tags', []),
                'placement_basis': actual,
            })

    scored_rows = [x for x in rows if x['placement_scored']]
    correct = sum(x['placement_correct'] for x in scored_rows)
    total = len(scored_rows)
    critical = [
        x for x in scored_rows
        if not x['placement_correct'] and '/03_PEOPLES/CULTURES/HEARTH/' in norm(x['document'])
    ]
    report = {
        'schema_version': '1.1',
        'mode': 'READ_ONLY',
        'purpose': 'measure canonical placement from identity_layer independently of relationship-label perfection',
        'cases': rows,
        'summary': {
            'documents': len(rows),
            'scored_documents': total,
            'unscored_documents': len(rows) - total,
            'correct_placements': correct,
            'incorrect_placements': total - correct,
            'placement_accuracy': round(correct / total, 3) if total else None,
            'critical_wrong_hearth_placements': len(critical),
            'placement_source': 'identity.identity_layer',
            'scope_region_is_specialization_only': True,
            'relationship_tag_is_not_placement_gate': True,
        },
        'safety': {
            'automatic_move': False,
            'automatic_canon_change': False,
            'human_validation_required': True,
        },
    }
    (root / 'CORE_PLACEMENT_BENCHMARK.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report['summary'], indent=2))

if __name__ == '__main__':
    main()
