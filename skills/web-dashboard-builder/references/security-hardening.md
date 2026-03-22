# Security Hardening for Intelligence Dashboards

## Threat Model

**Primary Threat:** Competitors scraping proprietary intelligence data

**Attack Vectors:**
1. View Source → copy embedded data
2. Save HTML → parse static data
3. Scrape rendered content
4. Bulk API requests

## Security Strategy

### Layer 1: Portal Authentication

Password-protected gateway prevents unauthorized access.

```javascript
// middleware.ts - Next.js
import { NextResponse } from 'next/server';

export function middleware(request) {
  const session = request.cookies.get('session');
  const isProtected = request.nextUrl.pathname.startsWith('/dashboard');
  
  if (isProtected && !session) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
}
```

### Layer 2: Protected Data Endpoints

JSON files served only to authenticated users.

**Vercel Headers (vercel.json):**
```json
{
  "routes": [
    {
      "src": "/data/(.*)",
      "headers": {
        "Cache-Control": "private, no-store"
      }
    }
  ]
}
```

**Next.js Route Handler:**
```typescript
// app/api/data/portfolio/route.ts
import { cookies } from 'next/headers';

export async function GET() {
  const session = cookies().get('session');
  if (!session) {
    return new Response('Unauthorized', { status: 401 });
  }
  
  const data = await getPortfolioData();
  return Response.json(data);
}
```

### Layer 3: Fetch with Credentials

Ensure cookies/session sent with requests.

```javascript
// DataLoader with auth
const DataLoader = {
  async load(file) {
    const response = await fetch(`api/data/${file}`, {
      credentials: 'include',  // Send cookies
      headers: {
        'Accept': 'application/json'
      }
    });
    
    if (response.status === 401) {
      window.location.href = '/login';
      return;
    }
    
    return response.json();
  }
};
```

## Data Exposure Risks

### Risk: Browser DevTools

**Even with auth, logged-in users can:**
- View Network tab → see JSON responses
- Copy/paste data

**Mitigations:**
- Session timeouts (auto-logout)
- Rate limiting
- Watermarking (track which user accessed what)

### Risk: Screenshots

**User can screenshot rendered dashboard.**

**Acceptance:** This is unavoidable. Focus on:
- Preventing bulk extraction
- Legal terms of use
- Time-limited access

## Implementation Checklist

- [ ] Portal requires login
- [ ] Session expires after 1 week
- [ ] JSON endpoints require auth
- [ ] No sensitive data in HTML/JS
- [ ] API routes rate-limited
- [ ] CORS configured properly
- [ ] No caching of JSON data
- [ ] HTTPS only

## Deployment Patterns

### Pattern 1: Vueroo-Style Portal

**Architecture:**
- Next.js with auth
- Static dashboard files in `/public/`
- API routes for data
- Server-side auth checks

**Pros:** Simple, proven
**Cons:** Dashboard files publicly accessible (empty shell)

### Pattern 2: Fully Server-Rendered

**Architecture:**
- Data injected server-side
- HTML rendered with data
- No client-side JSON fetch

**Pros:** Zero exposed endpoints
**Cons:** Harder to build, requires full-stack

### Pattern 3: Hybrid (Recommended)

**Architecture:**
- Static dashboard shell
- API routes for data (authenticated)
- Server components for initial load
- Client fetch for updates

```typescript
// Server component loads initial data
export default async function Dashboard() {
  const session = await getSession();
  if (!session) redirect('/login');
  
  const data = await getData(); // Server-side
  
  return <ClientDashboard initialData={data} />;
}

// Client component fetches updates
function ClientDashboard({ initialData }) {
  const [data, setData] = useState(initialData);
  
  const refresh = async () => {
    const newData = await fetch('/api/data', {
      credentials: 'include'
    }).then(r => r.json());
    setData(newData);
  };
}
```

## Anti-Scraping Techniques

### Rate Limiting

```typescript
// middleware.ts
import { rateLimiter } from './lib/rate-limit';

export async function middleware(request) {
  if (request.nextUrl.pathname.startsWith('/api/data')) {
    const limit = await rateLimiter.check(request);
    if (!limit.success) {
      return new Response('Rate limit exceeded', { status: 429 });
    }
  }
}
```

### Data Chunking

Don't return entire dataset at once:

```javascript
// Paginated API
fetch('/api/data?page=1&limit=50');
```

### Obfuscation (Not Recommended)

**Why we don't do this:**
- Gives false sense of security
- Easy to reverse
- Adds complexity
- Hurts performance

**Better:** Proper authentication

## Legal Protections

**Terms of Service:**
- No scraping clause
- Proprietary data notice
- Account termination for violations

**Technical + Legal = Defense in Depth**

## Summary

| Approach | Security | Complexity | Recommendation |
|----------|----------|------------|----------------|
| Embedded data | ❌ None | Low | Never use |
| JSON + auth | ✅ Good | Medium | Use this |
| Server-rendered | ✅ Best | High | Consider |
| Obfuscation | ❌ Fake | Medium | Never use |

**Key principle:** HTML/JS should be worthless without authentication.
