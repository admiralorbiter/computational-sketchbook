def audit(actor, action, entity, entity_id=None, note=None):
    # v0: print to stdout; later write to DB table 'audit'
    print(f"[AUDIT] {actor} {action} {entity} {entity_id or ''} {note or ''}")
