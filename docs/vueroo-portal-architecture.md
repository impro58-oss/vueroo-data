# VUEROO.COM - Portal Architecture
## Sovereign Intelligence Platform

**Concept:** Multi-tenant membership portal delivering specialized intelligence dashboards (Crypto, MedTech, etc.) with tiered access control.

**Domain:** vueroo.com
**Tagline:** "Intelligence for the Sovereign Investor"

---

## CORE CONCEPT

### What It Is
A membership-based intelligence platform where subscribers pay for access to specialized data dashboards built on proprietary analysis systems (TrojanLogic4H, NeuroVue, etc.)

### User Tiers

| Tier | Role | Access | Price Range |
|------|------|--------|-------------|
| **Roo (Admin)** | Master view | All silos + admin panel | N/A |
| **Crypto Trader** | Single silo | CryptoVue dashboard only | $49-99/mo |
| **MedTech Analyst** | Single silo | NeuroVue dashboard only | $79-149/mo |
| **Full Stack** | Multi-silo | All current + future silos | $199-299/mo |
| **Enterprise** | API access | All data via API + dashboards | $500+/mo |

### Silo Structure
Each silo is an isolated intelligence vertical:
- **CryptoVue** - Crypto market intelligence (LIVE)
- **NeuroVue** - Neurovascular medtech intelligence (LIVE)
- **Future:** EnergyVue, AeroVue, BioVue, etc.

---

## TECHNOLOGY ARCHITECTURE

### Frontend Stack
```
Framework: Next.js 14+ (App Router)
Language: TypeScript
Styling: Tailwind CSS + shadcn/ui
State: Zustand / React Query
Charts: Chart.js / Recharts / TradingView Widget API
Maps: D3.js / Leaflet (for regional heatmaps)
```

### Backend Stack
```
Runtime: Node.js (Next.js API routes + Edge functions)
Auth: Clerk (preferred) or Supabase Auth
Database: Supabase PostgreSQL
Cache: Redis (Upstash) or Vercel KV
Queue: Inngest (for background jobs)
Storage: Supabase Storage (for PDFs, exports)
```

### Payment & Billing
```
Gateway: Stripe
Subscriptions: Stripe Billing
Invoices: Stripe + email via Resend
Tax: Stripe Tax or TaxJar
```

### External Integrations
```
TradingView: Embeddable charts via Widget API
Notion: Internal data sync (already built)
Crypto Data: Binance API, CoinGlass API
MedTech Data: FDA APIs, ClinicalTrials.gov
Email: Resend or SendGrid
Analytics: Plausible (privacy-focused)
```

---

## DATABASE SCHEMA

### Users Table
```sql
create table users (
  id uuid primary key default gen_random_uuid(),
  email varchar(255) unique not null,
  clerk_id varchar(255) unique, -- for Clerk auth
  full_name varchar(255),
  role varchar(50) default 'subscriber', -- admin, subscriber
  tier varchar(50), -- crypto_only, medtech_only, full_stack, enterprise
  subscription_status varchar(50), -- active, paused, cancelled, past_due
  stripe_customer_id varchar(255),
  stripe_subscription_id varchar(255),
  current_period_end timestamp,
  created_at timestamp default now(),
  last_login timestamp
);
```

### Silos Table (Access Control)
```sql
create table silos (
  id uuid primary key default gen_random_uuid(),
  slug varchar(50) unique not null, -- cryptovue, neurovue
  name varchar(100) not null,
  description text,
  is_active boolean default true,
  monthly_price integer, -- in cents
  yearly_price integer,
  requires_invite boolean default false
);

-- Seed data
insert into silos (slug, name, description, monthly_price) values
('cryptovue', 'CryptoVue Intelligence', 'Real-time crypto market analysis with TrojanLogic4H signals', 9900),
('neurovue', 'NeuroVue Intelligence', 'Neurovascular medtech competitive intelligence', 14900);
```

### User Silo Access (Junction Table)
```sql
create table user_silo_access (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  silo_id uuid references silos(id) on delete cascade,
  granted_at timestamp default now(),
  expires_at timestamp,
  access_type varchar(50) default 'subscription', -- subscription, trial, comped
  unique(user_id, silo_id)
);
```

### Dashboard Config (Per Silo)
```sql
create table dashboard_configs (
  id uuid primary key default gen_random_uuid(),
  silo_id uuid references silos(id) on delete cascade,
  component_key varchar(100) not null, -- heatmap, signals_table, portfolio
  component_type varchar(50), -- chart, table, map, metric
  config jsonb, -- flexible configuration per component
  sort_order integer default 0
);
```

### Activity Log
```sql
create table activity_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  action varchar(100) not null, -- view_dashboard, export_data, login
  silo_id uuid references silos(id),
  metadata jsonb,
  ip_address inet,
  user_agent text,
  created_at timestamp default now()
);
```

### Invoices
```sql
create table invoices (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  stripe_invoice_id varchar(255) unique,
  amount_due integer, -- in cents
  amount_paid integer,
  status varchar(50), -- draft, open, paid, void, uncollectible
  period_start timestamp,
  period_end timestamp,
  paid_at timestamp,
  pdf_url text,
  created_at timestamp default now()
);
```

---

## API ARCHITECTURE

### Authentication Flow
1. User clicks "Sign In" → Redirect to Clerk hosted UI
2. Clerk handles OAuth (Google, email, etc.) → Returns JWT
3. Frontend stores JWT in httpOnly cookie
4. API routes validate JWT via Clerk middleware
5. Server components get user via `auth()` helper

### Protected Route Middleware
```typescript
// middleware.ts
import { authMiddleware } from "@clerk/nextjs";
 
export default authMiddleware({
  publicRoutes: ["/", "/sign-in", "/sign-up", "/pricing"],
  afterAuth(auth, req, evt) {
    // Check if user has access to requested silo
    if (req.nextUrl.pathname.startsWith('/dashboard/')) {
      const silo = req.nextUrl.pathname.split('/')[2];
      if (!auth.userId) return redirectToSignIn({ returnBackUrl: req.url });
      // Check silo access in database
    }
  }
});
```

### API Endpoints

#### Auth
```
POST   /api/auth/webhook        # Clerk webhook (sync user to DB)
```

#### User
```
GET    /api/user/me             # Current user profile
PATCH  /api/user/me             # Update profile
GET    /api/user/access         # Get user's silo access list
GET    /api/user/invoices       # Get billing history
```

#### Dashboard Data (Protected by silo access)
```
GET    /api/silo/:slug/config          # Dashboard configuration
GET    /api/silo/:slug/data/latest     # Latest scan data
GET    /api/silo/:slug/data/history    # Historical data
GET    /api/silo/:slug/data/export     # CSV/JSON export
```

#### Stripe Webhooks
```
POST   /api/webhooks/stripe     # Handle subscription events
```

---

## FRONTEND ARCHITECTURE

### Route Structure
```
/                          # Marketing landing page
/pricing                   # Pricing table with tier comparison
/sign-in                   # Clerk auth page
/sign-up                   # Clerk registration

/dashboard                 # Redirect to first available silo
/dashboard/cryptovue       # CryptoVue dashboard (protected)
/dashboard/neurovue       # NeuroVue dashboard (protected)
/dashboard/admin          # Admin panel (Roo only)

/account/settings         # User profile, billing, password
/account/billing           # Invoices, payment methods
/account/subscription     # Upgrade/downgrade/cancel
```

### Component Hierarchy
```
app/
├── (marketing)/            # Public routes
│   ├── page.tsx           # Landing page
│   ├── pricing/page.tsx
│   └── layout.tsx
├── (dashboard)/            # Protected routes
│   ├── layout.tsx         # Dashboard shell with sidebar
│   ├── dashboard/page.tsx # Redirect logic
│   ├── dashboard/
│   │   ├── [silo]/
│   │   │   └── page.tsx   # Dynamic silo dashboard
│   │   └── admin/
│   │       └── page.tsx   # Admin panel
│   └── account/
│       ├── settings/page.tsx
│       ├── billing/page.tsx
│       └── subscription/page.tsx
├── api/
│   └── ...                # API routes
├── components/
│   ├── ui/               # shadcn components
│   ├── dashboard/        # Dashboard-specific components
│   │   ├── HeatMap.tsx
│   │   ├── SignalTable.tsx
│   │   ├── StatCards.tsx
│   │   └── PortfolioTracker.tsx
│   └── marketing/        # Landing page components
├── lib/
│   ├── db/              # Database helpers
│   ├── auth/            # Auth utilities
│   ├── stripe/          # Stripe client
│   └── utils/           # General utilities
└── types/
    └── index.ts         # TypeScript definitions
```

### Key Components

#### Dashboard Shell (Layout)
```typescript
// components/dashboard/DashboardShell.tsx
interface DashboardShellProps {
  silo: string;
  children: React.ReactNode;
}

// Shows:
// - Sidebar with available silos (based on user access)
// - User dropdown (profile, billing, logout)
// - Silo switcher (if multi-silo access)
// - Real-time notification bell (new signals)
```

#### Silo Router
```typescript
// Dynamically loads correct dashboard based on silo slug
const siloComponents = {
  cryptovue: CryptoVueDashboard,
  neurovue: NeuroVueDashboard,
};

// Each silo dashboard fetches its own config from DB
// Config determines which widgets to show and their order
```

---

## SECURITY CONSIDERATIONS

### Data Protection
- **Row Level Security (RLS)** on all tables
- User can only see their own data
- API routes verify silo access before returning data

### Rate Limiting
```typescript
// Apply per-route rate limiting
import { rateLimit } from '@/lib/rate-limit';

const limiter = rateLimit({
  interval: 60 * 1000, // 1 minute
  uniqueTokenPerInterval: 500
});

// Free tier: 100 requests/min
// Paid tier: 1000 requests/min
```

### Content Security
- CSP headers prevent XSS
- API keys stored in environment variables only
- Database credentials via Supabase connection pooling
- No sensitive data in client-side code

### Subscription Enforcement
- Daily job checks subscription status
- Expired access → automatic downgrade to free tier
- Grace period of 3 days for failed payments

---

## DEPLOYMENT STRATEGY

### Phase 1: MVP (Week 1-2)
1. Set up Next.js project with Clerk + Supabase
2. Create landing page + pricing
3. Implement auth flow
4. Migrate CryptoVue dashboard (embed current HTML)
5. Stripe checkout for single silo
6. Deploy to Vercel

### Phase 2: Polish (Week 3-4)
1. Build user account pages
2. Add NeuroVue silo
3. Implement role-based navigation
4. Add activity logging
5. Admin panel for Roo

### Phase 3: Scale (Month 2+)
1. Migrate from embedded HTML to React components
2. Real-time WebSocket updates
3. API access for Enterprise tier
4. Affiliate/referral system
5. Automated email sequences

### Infrastructure Costs
| Service | Monthly Cost |
|---------|-------------|
| Vercel Pro | $20 |
| Supabase | $25 |
| Clerk | $0 (up to 10k users) |
| Stripe | 2.9% + 30¢ per transaction |
| Resend | $0 (up to 3k emails) |
| **Total Fixed** | **~$45/month** |

---

## MONETIZATION STRATEGY

### Pricing Psychology
- **CryptoVue:** $99/month (odd number = higher perceived value)
- **NeuroVue:** $149/month (medical data commands premium)
- **Full Stack:** $249/month (20% discount vs separate)
- **Annual:** 2 months free (encourage commitment)

### Trial Strategy
- 7-day free trial on all tiers
- No credit card required
- Auto-downgrade to "Free Preview" (limited data)
- Email sequence during trial to show value

### Upgrade Triggers
- User views 5+ pages → "Unlock full access"
- Exports data → "Export limit reached, upgrade"
- After 3 days → "Early adopter discount expires soon"

---

## UNIQUE SELLING PROPOSITIONS

1. **Proprietary Algorithms** - TrojanLogic4H not available elsewhere
2. **Multi-Asset Intelligence** - Crypto + MedTech in one platform
3. **Sovereign Approach** - No dependence on traditional financial media
4. **Curated Data** - You filter noise, members get signal
5. **Community** - Future: private Discord, monthly calls

---

## SUCCESS METRICS

| Metric | Target (6 months) |
|--------|-------------------|
| Free trials | 500 |
| Conversion rate | 15% |
| Paid subscribers | 75 |
| MRR | $7,500 |
| Churn rate | <5%/month |
| NPS score | >50 |

---

## FILES CREATED

- `/docs/vueroo-portal-architecture.md` (this file)
- Future: `/docs/vueroo-database-schema.sql`
- Future: `/docs/vueroo-api-spec.yaml`
- Future: `/docs/vueroo-wireframes.fig`

---

*Architecture Version: 1.0*
*Last Updated: 2026-03-19*
*Status: Ready for implementation*
