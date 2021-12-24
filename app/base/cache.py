from django.core.cache import cache
import json

def retrieve_cached_json(cache_key, fetch, force=False, expiration=600):
    cached = cache.get(cache_key)
    if not cached or force:
        data = fetch()
        cache.set(cache_key, json.dumps(data))
        return data
    else:
        return json.loads(cached)
