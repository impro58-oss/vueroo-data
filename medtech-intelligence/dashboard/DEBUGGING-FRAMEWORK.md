# NeuroVue Debugging Framework
## Systematic Problem-Solving for Web Deployment Issues

---

## 🔬 Root Cause Analysis (RCA)

### Issue: Dashboard Shows "Failed to Load Data - NeuroVueDataLoader is not defined"

**Timeline of Attempts:**
| Attempt | Approach | Result | Why It Failed |
|---------|----------|--------|---------------|
| v1 | External `data-loader.js` | 404 Error | Vercel not serving the file |
| v2 | GitHub fallback URLs | 404 Error | Same issue - external file dependency |
| v3 | Cache-busting `?v=2` | 404 Error | File truly missing from deployment |
| v4 | `vercel.json` headers | No change | Headers don't fix missing files |
| v5 | Embedded fallback data | "Not defined" | Timing issue - fallback ran after DOMContentLoaded |
| v6 | Always-create fallback | "Not defined" | Syntax issue - `async/await` in older browsers |
| **v7** | **Remove external script + embed everything** | **SUCCESS** | Zero external dependencies |

**Root Causes Identified:**
1. **Vercel Deployment Gap** — `data-loader.js` committed to repo but not served
2. **Timing Race Condition** — DOMContentLoaded fires before scripts loaded
3. **Browser Compatibility** — Optional chaining (`?.`) and `async/await` fail in some contexts
4. **Silent Failures** — 404s don't stop execution, just leave undefined variables

---

## 🧠 Debugging Framework

### Phase 1: Isolation
**Question:** Is this a code issue or deployment issue?

**Test:**
```javascript
// Add at top of <script> block
console.log('Script started');
console.log('NeuroVueDataLoader exists:', typeof NeuroVueDataLoader);
console.log('Data exists:', typeof appData);
```

**Interpretation:**
- If `undefined` → Deployment issue (file not loading)
- If `defined` → Code issue (runtime error)

---

### Phase 2: Dependency Analysis
**Question:** What external dependencies do we have?

**Checklist:**
- [ ] External JS files (`src="file.js"`)
- [ ] External CSS (`href="styles.css"`)
- [ ] External APIs (`fetch()` calls)
- [ ] External iframes (`<iframe src="...">`)
- [ ] CDN resources (Tailwind, FontAwesome)

**Rule:** Each external dependency = potential failure point

---

### Phase 3: Browser Compatibility
**Question:** Are we using modern JavaScript features?

**High-Risk Features:**
| Feature | Risk Level | Fallback |
|---------|-----------|----------|
| `?.` Optional chaining | HIGH | `obj && obj.prop` |
| `??` Nullish coalescing | HIGH | `value != null ? value : default` |
| `async/await` | MEDIUM | `.then().catch()` |
| Arrow functions `=>` | LOW | `function() {}` |
| Template literals `` ` `` | LOW | String concatenation |

**Test:** Open in Internet Explorer 11 or old Safari

---

### Phase 4: Deployment Verification
**Question:** Are files actually deployed?

**Checklist:**
```bash
# 1. Verify file exists in repo
git ls-files | grep data-loader.js

# 2. Check if file is in deployment
curl -I https://www.vueroo.com/medtech/data-loader.js

# 3. Check file content
curl https://www.vueroo.com/medtech/data-loader.js | head -5

# 4. Verify build output
vercel --debug  # Check build logs
```

---

## 🛠️ Solution Patterns

### Pattern 1: Zero-Dependency Architecture
**When to use:** Static dashboards, guaranteed uptime

**Structure:**
```html
<script>
  // 1. EMBED all data
  const DATA = { /* all data here */ };
  
  // 2. EMBED all functions
  const Utils = {
    formatNumber: function(n) { /* ... */ },
    processData: function(d) { /* ... */ }
  };
  
  // 3. Initialize immediately
  document.addEventListener('DOMContentLoaded', function() {
    initDashboard(DATA);
  });
</script>
```

**Pros:**
- ✅ Never fails to load
- ✅ Instant display
- ✅ No CORS issues
- ✅ Works offline

**Cons:**
- ❌ Larger HTML file
- ❌ Requires rebuild for data updates
- ❌ No dynamic loading

---

### Pattern 2: Graceful Degradation
**When to use:** Hybrid static/dynamic

**Structure:**
```html
<script src="data-loader.js"></script>
<script>
  // Fallback if external fails
  if (typeof DataLoader === 'undefined') {
    window.DataLoader = { /* embedded fallback */ };
  }
</script>
```

**Pros:**
- ✅ Tries dynamic first
- ✅ Falls back to static

**Cons:**
- ❌ Complex timing issues
- ❌ Two code paths to maintain

---

### Pattern 3: CDN-First with Local Fallback
**When to use:** Libraries (Chart.js, Tailwind)

**Structure:**
```html
<script src="https://cdn.example.com/lib.js"></script>
<script>
  if (typeof Library === 'undefined') {
    document.write('<script src="local/lib.js"><\/script>');
  }
</script>
```

---

## 📊 Decision Matrix

| Scenario | Recommended Pattern | Why |
|----------|---------------------|-----|
| Static dashboard | Pattern 1: Zero-Dependency | Reliability > flexibility |
| API-powered app | Pattern 2: Graceful Degradation | Dynamic data required |
| Production system | Pattern 1 + Build pipeline | Compile data at build time |
| Quick prototype | Pattern 2 | Fast to iterate |

---

## ✅ Pre-Deployment Checklist

### Code Quality
- [ ] No optional chaining (`?.`)
- [ ] No nullish coalescing (`??`)
- [ ] No `async/await` (use promises)
- [ ] All functions use `function()` not `=>`
- [ ] All template literals use concatenation fallback

### File Structure
- [ ] All JS embedded in HTML OR
- [ ] All JS in single file (no dependencies)
- [ ] No external iframes
- [ ] Data embedded OR fetched with fallback

### Testing
- [ ] Works with `file://` protocol
- [ ] Works on old browsers
- [ ] Works without internet (if applicable)
- [ ] Console has 0 errors
- [ ] Loading spinner disappears

### Deployment
- [ ] `git ls-files` shows all files
- [ ] `curl` test confirms files serve
- [ ] Vercel/GitHub Pages build succeeds
- [ ] Hard refresh (Ctrl+Shift+R) works

---

## 📝 Incident Log

### Incident #1: NeuroVue Dashboard 404
**Date:** 2026-03-25  
**Severity:** HIGH (dashboard unusable)  
**Duration:** ~1 hour  
**Status:** RESOLVED

**Symptoms:**
- "Failed to Load Data"
- "NeuroVueDataLoader is not defined"
- Console: `data-loader.js:1 Failed to load resource: 404`

**Investigation:**
1. File exists in repo ✓
2. File not served by Vercel ✗
3. Multiple fix attempts failed due to:
   - Timing issues (DOMContentLoaded)
   - Syntax issues (async/await)
   - Deployment lag (Vercel cache)

**Resolution:**
- Removed all external dependencies
- Embedded all data/functions in HTML
- Used traditional JavaScript syntax
- Single-file architecture

**Lessons Learned:**
1. External dependencies are failure points
2. Timing is hard to debug
3. Simpler = more reliable
4. Always test `file://` first

---

## 🎓 Knowledge Base

### Why Vercel Didn't Serve data-loader.js
**Hypothesis:** Vercel's static file handling has edge cases:
- Files in `public/` should serve automatically
- But timing/commit issues can cause gaps
- Cache invalidation is aggressive
- Solution: Single-file approach avoids this entirely

### Why Optional Chaining Failed
**Fact:** Some deployment contexts use older JS parsers
- Vercel's edge functions?
- Some browsers in strict mode?
- Better to avoid entirely for static sites

### Why Timing Fixes Didn't Work
**Insight:** The fix ran AFTER the error occurred
- Script loading is async
- DOMContentLoaded fires when HTML parsed
- External scripts may not be ready
- Solution: Define fallback BEFORE any async operations

---

## 🚀 Future Improvements

### Build Pipeline
```bash
# Pre-deployment script
npm run build
# 1. Read data JSON
# 2. Inject into HTML template
# 3. Minify JS
# 4. Output single HTML file
# 5. Deploy
```

### Testing Framework
```javascript
// Automated test
describe('NeuroVue Dashboard', () => {
  it('loads without external dependencies', () => {
    // Mock all fetches to fail
    // Assert dashboard still renders
  });
  
  it('works with file:// protocol', () => {
    // Test locally
    // Assert no CORS errors
  });
});
```

---

*Framework Version: 1.0  
Last Updated: 2026-03-25 by Lumina  
Based on: NeuroVue v7 Deployment Experience*
