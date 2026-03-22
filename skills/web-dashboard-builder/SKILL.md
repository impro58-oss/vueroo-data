---
name: web-dashboard-builder
description: Build HTML dashboards with dynamic JSON data loading. Use when: (1) Creating data-driven HTML dashboards that fetch from JSON files, (2) Building tables/charts that render from external data sources, (3) Implementing filter systems with dynamic data, (4) Troubleshooting fetch/CORS issues, (5) Creating dashboard navigation between multiple pages, (6) Deploying dashboards to web servers or portals. NOT for embedded/static data dashboards.
---

# Web Dashboard Builder

## Architecture Principle

**All data loads dynamically from JSON files.**

- Dashboards require an HTTP server (cannot run via `file://`)
- Updates are made by editing JSON files only
- HTML/CSS/JS remain static
- Clean separation: data layer vs presentation layer

## Project Structure

```
dashboard/
├── index.html              # Main entry point
├── data/                   # JSON data files
│   ├── portfolio.json
│   ├── revenue.json
│   └── heatmap-data.json
├── css/
│   └── styles.css
├── js/
│   ├── main.js            # App initialization
│   ├── data-loader.js     # Fetch and cache JSON
│   ├── filters.js         # Filter logic
│   └── renderers.js       # Table/chart rendering
└── pages/                 # Additional views
    ├── portfolio.html
    └── revenue.html
```

## Data Loading Pattern

### Core Loader Module

```javascript
// js/data-loader.js
const DataLoader = {
  cache: {},
  
  async load(file) {
    if (this.cache[file]) {
      return this.cache[file];
    }
    
    try {
      const response = await fetch(`data/${file}.json`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      this.cache[file] = data;
      return data;
    } catch (error) {
      console.error(`Failed to load ${file}.json:`, error);
      this.showError(`Failed to load data. Please refresh.`);
      throw error;
    }
  },
  
  showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
      errorDiv.textContent = message;
      errorDiv.style.display = 'block';
    }
  },
  
  clearCache() {
    this.cache = {};
  }
};
```

### Usage in Dashboard

```javascript
// js/main.js
async function init() {
  showLoading();
  
  try {
    const [portfolio, revenue] = await Promise.all([
      DataLoader.load('portfolio'),
      DataLoader.load('revenue')
    ]);
    
    renderPortfolio(portfolio);
    renderRevenue(revenue);
    setupFilters(portfolio);
    
    hideLoading();
  } catch (error) {
    console.error('Initialization failed:', error);
  }
}

document.addEventListener('DOMContentLoaded', init);
```

## JSON Schema Standards

### Portfolio Matrix Data

```json
{
  "version": "2026-03",
  "lastUpdated": "2026-03-19",
  "categories": [
    {
      "id": "coils",
      "name": "Embolization Coils",
      "segment": "hemorrhagic",
      "segmentName": "Hemorrhagic Stroke"
    }
  ],
  "companies": [
    { "id": "medtronic", "name": "Medtronic", "color": "#003087" },
    { "id": "stryker", "name": "Stryker", "color": "#00a9e0" }
  ],
  "products": [
    {
      "categoryId": "coils",
      "wallaby": { "name": "Lumina Coils", "status": "available" },
      "competitors": {
        "medtronic": { "name": "Target 360", "status": "available" },
        "stryker": { "name": "GDC 360", "status": "available" }
      },
      "isGap": false
    }
  ]
}
```

### Status Values

- `"available"` — Product exists
- `"gap"` — No product in this category
- `"development"` — In development
- `"limited"` — Limited availability

## Filter System

### Filter State Management

```javascript
// js/filters.js
const FilterState = {
  view: 'all',           // all | gaps | wallaby-only
  category: 'all',       // all | category-id
  segment: 'all',        // all | segment-id
  company: 'all'         // all | company-id
};

const FilterFunctions = {
  view(product) {
    if (FilterState.view === 'gaps') return product.isGap;
    if (FilterState.view === 'wallaby-only') return product.wallaby?.status === 'available';
    return true;
  },
  
  category(product, categories) {
    if (FilterState.category === 'all') return true;
    const cat = categories.find(c => c.id === FilterState.category);
    return product.categoryId === FilterState.category;
  },
  
  segment(product, categories) {
    if (FilterState.segment === 'all') return true;
    const cat = categories.find(c => c.id === product.categoryId);
    return cat?.segment === FilterState.segment;
  }
};

function applyFilters(products, categories) {
  return products.filter(product => {
    return Object.values(FilterFunctions).every(fn => fn(product, categories));
  });
}
```

### Filter UI Binding

```javascript
function setupFilters(data) {
  const viewSelect = document.getElementById('view-filter');
  const categorySelect = document.getElementById('category-filter');
  const segmentSelect = document.getElementById('segment-filter');
  
  // Populate dropdowns
  populateSelect(categorySelect, data.categories, 'id', 'name');
  populateSelect(segmentSelect, 
    [...new Set(data.categories.map(c => ({ id: c.segment, name: c.segmentName })))],
    'id', 'name'
  );
  
  // Bind events
  viewSelect.addEventListener('change', (e) => {
    FilterState.view = e.target.value;
    renderTable(data);
  });
  
  categorySelect.addEventListener('change', (e) => {
    FilterState.category = e.target.value;
    renderTable(data);
  });
}

function populateSelect(select, items, valueKey, labelKey) {
  select.innerHTML = '<option value="all">All</option>' +
    items.map(item => `<option value="${item[valueKey]}">${item[labelKey]}</option>`).join('');
}
```

## Table Rendering

### Dynamic Table Generation

```javascript
function renderTable(data) {
  const tbody = document.querySelector('#matrix-body');
  const filtered = applyFilters(data.products, data.categories);
  
  tbody.innerHTML = filtered.map(product => {
    const category = data.categories.find(c => c.id === product.categoryId);
    const isGap = product.isGap || !product.wallaby?.name;
    
    return `
      <tr class="${isGap ? 'gap-row' : ''}" data-category="${product.categoryId}">
        <td class="category-cell">
          <span class="segment-badge" style="background:${category?.color || '#ccc'}">
            ${category?.segmentName || 'Unknown'}
          </span>
          ${category?.name}
        </td>
        <td class="wallaby-cell">
          ${renderProductCell(product.wallaby)}
        </td>
        ${data.companies.map(comp => `
          <td class="competitor-cell">
            ${renderProductCell(product.competitors?.[comp.id])}
          </td>
        `).join('')}
      </tr>
    `;
  }).join('');
}

function renderProductCell(product) {
  if (!product || product.status === 'gap') {
    return '<span class="status-gap"><i class="fas fa-times"></i> Gap</span>';
  }
  const statusClass = `status-${product.status}`;
  return `<span class="${statusClass}"><i class="fas fa-check"></i> ${product.name}</span>`;
}
```

## Development Workflow

### Local Development Server

```bash
# Python 3
python -m http.server 8000

# Node.js
npx http-server -p 8000

# PHP
php -S localhost:8000
```

Access via `http://localhost:8000` — NOT `file://`

### Monthly Update Process

1. Edit JSON files in `/data/` directory
2. Test locally with dev server
3. Commit changes
4. Deploy to portal/server
5. Clear browser cache if needed

## Portal Integration (Next.js)

### File Structure

```
portal/
├── app/
│   └── dashboard/
│       ├── page.tsx              # Overview
│       ├── neurovue/
│       │   └── page.tsx          # Redirect to static
│       └── cryptovue/
│           └── page.tsx
├── public/
│   ├── neuro/
│   │   ├── index.html
│   │   ├── data/
│   │   │   └── portfolio.json
│   │   └── ...
│   └── crypto/
│       └── ...
```

### Redirect Pattern

```typescript
// app/dashboard/neurovue/page.tsx
import { redirect } from 'next/navigation';

export default function NeuroVueRedirect() {
  redirect('/neuro/index.html');
}
```

### JSON Serving

Vercel/Next.js automatically serves files from `/public/`:
- `/public/neuro/data/portfolio.json` → `https://site.com/neuro/data/portfolio.json`

## Error Handling

### Loading States

```html
<div id="app">
  <div id="loading" class="loading-overlay">
    <div class="spinner"></div>
    <p>Loading dashboard data...</p>
  </div>
  
  <div id="error" class="error-message" style="display:none">
    <i class="fas fa-exclamation-triangle"></i>
    <p>Failed to load data. <button onclick="location.reload()">Retry</button></p>
  </div>
  
  <div id="dashboard" style="display:none">
    <!-- Dashboard content -->
  </div>
</div>
```

### Fetch Retry Logic

```javascript
async function fetchWithRetry(url, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url);
      if (response.ok) return response;
      throw new Error(`HTTP ${response.status}`);
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(r => setTimeout(r, 1000 * (i + 1))); // Exponential backoff
    }
  }
}
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Failed to fetch" | Running via file:// | Use local server |
| 404 on JSON | Wrong path | Check relative paths from HTML |
| CORS error | Cross-origin request | Ensure same origin or proper headers |
| Data not updating | Browser cache | Hard refresh (Ctrl+Shift+R) |
| Slow initial load | Large JSON | Implement chunked loading or caching |

## Security Considerations

### Why JSON-Only Architecture?

**Data Protection:**
- HTML/JS contains no proprietary data — only presentation logic
- JSON endpoints can be protected (auth headers, cookies)
- Scrapers see empty shell without authentication

**vs Embedded Data:**
```javascript
// BAD: Data in HTML (easily scraped)
const competitors = [{ name: "Secret Product", price: 999 }];

// GOOD: Data fetched from protected endpoint
// Scraper sees: fetch('/api/data') — empty without auth
```

### Protection Layers

1. **Portal Authentication** — Password-protected gateway
2. **Session Cookies** — Required for JSON fetch
3. **Rate Limiting** — Prevent bulk scraping
4. **No Public JSON URLs** — Data endpoints behind auth

### What We Don't Do

- ❌ Embed data in JavaScript
- ❌ Use client-side encryption (pointless)
- ❌ Obfuscation (ineffective)
- ❌ Static data in HTML

### What We Do

- ✅ Serve HTML shell publicly (no data)
- ✅ Protect JSON endpoints with auth
- ✅ Fetch after authentication
- ✅ Cache in memory only (not localStorage for sensitive data)

## References

- [json-standards.md](references/json-standards.md) — Complete JSON schema documentation
- [filter-patterns.md](references/filter-patterns.md) — Advanced filter implementations
- [portal-deployment.md](references/portal-deployment.md) — Next.js/Vercel deployment guide
- [security-hardening.md](references/security-hardening.md) — Authentication and data protection
