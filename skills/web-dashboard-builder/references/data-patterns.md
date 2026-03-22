# JSON Data Loading Patterns

## Three Approaches Compared

### 1. Embedded Data (Local Files)

**Use when:** Testing locally, single file distribution, no server

```javascript
// data.js
const portfolioData = {
  categories: [
    { id: "coils", name: "Embolization Coils", segment: "hemorrhagic" },
    { id: "flow_diverters", name: "Flow Diverters", segment: "hemorrhagic" },
    // ... 29 total
  ],
  competitors: {
    medtronic: ["Target Coils", "Pipeline", "Solitaire"],
    stryker: ["GDC Coils", "Surpass"],
    // ...
  },
  products: [
    { 
      category: "coils", 
      wallaby: "Lumina Coils", 
      medtronic: "Target 360",
      stryker: "GDC 360"
    },
    // ...
  ]
};
```

**HTML:**
```html
<script src="data.js"></script>
<script>
  // Data available immediately
  console.log(portfolioData.categories);
</script>
```

**Pros:**
- ✅ Works with `file://` protocol
- ✅ No async/await needed
- ✅ Zero network requests
- ✅ Always available

**Cons:**
- ❌ Harder to update (edit JS file)
- ❌ Mixes data and code
- ❌ Larger file size
- ❌ No syntax highlighting for JSON

---

### 2. External JSON (Server Required)

**Use when:** Production deployment, frequent updates, clean architecture

```javascript
// data.json
{
  "categories": [...],
  "competitors": {...},
  "products": [...]
}
```

**HTML:**
```html
<script>
  let portfolioData;
  
  async function loadData() {
    const response = await fetch('data.json');
    portfolioData = await response.json();
    renderDashboard();
  }
  
  loadData();
</script>
```

**Pros:**
- ✅ Clean separation of concerns
- ✅ Easy to update (replace JSON file)
- ✅ Cacheable by browser
- ✅ Syntax highlighting

**Cons:**
- ❌ Requires HTTP server (CORS blocks `file://`)
- ❌ Async complexity (handle loading states)
- ❌ Network dependency
- ❌ Potential fetch failures

---

### 3. Dual-Mode Hybrid (Recommended)

**Use when:** Need both local testing and production deployment

```javascript
// data.js - include this file
const embeddedData = {
  categories: [...],
  products: [...]
};
```

```javascript
// dashboard.js - main logic
let portfolioData;

async function init() {
  const isLocal = window.location.protocol === 'file:';
  
  if (isLocal) {
    // Use embedded data
    portfolioData = embeddedData;
  } else {
    // Fetch from server
    const response = await fetch('data.json');
    portfolioData = await response.json();
  }
  
  renderDashboard();
}

init();
```

**Build script for updates:**

```javascript
// build.js - converts JSON to JS
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('data.json', 'utf8'));

const jsContent = `const embeddedData = ${JSON.stringify(data, null, 2)};`;
fs.writeFileSync('data.js', jsContent);
```

**Pros:**
- ✅ Works in both environments
- ✅ Monthly updates: edit JSON → run build → deploy
- ✅ Clean code without `if/else` scattered everywhere

**Cons:**
- ⚠️ Slightly more complex setup
- ⚠️ Need build step

---

## Error Handling Patterns

### Fetch with Fallback

```javascript
async function loadData() {
  try {
    // Try server first
    const response = await fetch('data.json');
    if (!response.ok) throw new Error('HTTP ' + response.status);
    return await response.json();
  } catch (e) {
    console.warn('Server fetch failed, using fallback:', e);
    // Use embedded data
    return embeddedData;
  }
}
```

### Loading State

```html
<div id="loading">Loading data...</div>
<div id="error" style="display:none; color:red">Failed to load</div>
<div id="dashboard" style="display:none">...</div>

<script>
async function init() {
  try {
    const data = await loadData();
    document.getElementById('loading').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    render(data);
  } catch (e) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('error').style.display = 'block';
    console.error(e);
  }
}
</script>
```

---

## Data Structure Best Practices

### Normalized vs Denormalized

**Denormalized (easier to render):**
```javascript
const products = [
  { category: "Coils", company: "Medtronic", name: "Target 360" },
  { category: "Coils", company: "Stryker", name: "GDC 360" }
];
```

**Normalized (easier to update):**
```javascript
const categories = { coils: "Embolization Coils" };
const companies = { medtronic: "Medtronic" };
const products = [
  { categoryId: "coils", companyId: "medtronic", name: "Target 360" }
];
```

**For dashboards:** Use denormalized. Easier to render tables directly.

### Category Constants

```javascript
const SEGMENTS = {
  HEMORRHAGIC: { id: 'hemorrhagic', name: 'Hemorrhagic Stroke', color: '#ef4444' },
  ISCHEMIC: { id: 'ischemic', name: 'Ischemic Stroke', color: '#3b82f6' },
  ATHEROSCLEROSIS: { id: 'atherosclerosis', name: 'Atherosclerosis', color: '#10b981' }
};

const CATEGORIES = [
  { id: 'coils', name: 'Embolization Coils', segment: 'hemorrhagic' },
  { id: 'flow_diverters', name: 'Flow Diverters', segment: 'hemorrhagic' },
  // ...
];
```

---

## Monthly Update Workflow

1. **Edit** `data.json` with new information
2. **Run** build script: `node build.js`
3. **Commit** both `data.json` and `data.js`
4. **Deploy** to portal
5. **Test** local version with embedded data

**One-file alternative for non-technical users:**
- Edit only `data.js` directly
- No build step needed
- Simpler but mixes JSON/JS syntax
