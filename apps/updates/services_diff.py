def diff_proposals(old, new):
    old_set = {p["proposal_type"] for p in old}
    new_set = {p["proposal_type"] for p in new}

    return {
        "added": list(new_set - old_set),
        "removed": list(old_set - new_set),
        "unchanged": list(old_set & new_set),
    }
