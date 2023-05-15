import hashlib
import json


def get_score(store, phone, email, birthday=None, gender=None, first_name=None, last_name=None):
    # (phone + email) or (first_name  + last_name ) or (birthday + gender)
    key_parts = [
        first_name or '',
        last_name or '',
        str(phone) or '',
        birthday or '',
    ]
    key = 'uid:' + hashlib.md5(''.join(key_parts).encode()).hexdigest()
    
    score = store.get(key) or 0
    if score is not None:
        return score
    
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    
    # Cache for 60 minutes
    store.set(key, score, 60 * 60)
    return score


def get_interests(store, cid):
    r = store.get('i:{}'.format(cid))
    return json.loads(r) if r else []
