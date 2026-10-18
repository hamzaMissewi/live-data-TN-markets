# Live data dashboards: full plan, architecture, and tools

You already have the hardest part: a Python pipeline that scrapes 5 years of BVMT daily OHLCV for 60+ companies. That is the seed dataset. The plan below turns it into a public, indexable product, with your anomaly detection as the differentiator no competitor has.

## 1. Product definition

**Working concept:** a Tunisia-first (then MENA) markets and rates hub.

| Module | Pages generated | Update frequency |
|---|---|---|
| BVMT stocks (60+ companies) | 1 page per company, plus Tunindex, sectors, top gainers/losers, volume leaders | Daily after close |
| Currency rates (TND/EUR/USD/…) | Pair pages, converter pages, historical charts | Hourly |
| Gold, fuel, commodities | Price pages, local-unit conversions | Daily |
| Market anomalies (your edge) | "Unusual volume today" feed, per-stock anomaly history | Daily |
| Calculators (phase 2) | Net salary, loan, VAT | Static |

Your anomaly watchlist is a unique, hard-to-copy content type. Present it as "statistical outliers, not accusations", as you already frame it, which also keeps you safe legally.

## 2. Architecture

```
 Data sources ──► Ingestion (Python) ──► PostgreSQL + Redis ──► API (FastAPI or Django)
 (BVMT, BCT,      Celery/cron jobs        (TimescaleDB          │
  FX APIs, news)  validate + normalize     extension)           ▼
                                                          Next.js (ISR/SSG)
                                                                │
                                                       CDN (Cloudflare) ──► Users + Googlebot
```

**Layers**

1. **Ingestion:** scrapers and API clients on a schedule. Every run validates data (no null prices, no 50% jumps without a flag), stores the raw payload, then writes normalized rows. Keep raw snapshots so you can recompute later.
2. **Storage:** PostgreSQL with the TimescaleDB extension for time series. Redis for caching latest quotes and rate limiting.
3. **Analytics:** your pandas z-score pipeline runs after each ingestion and writes anomalies and "explained by news" flags to tables.
4. **API:** read-only JSON endpoints (`/stocks/{ticker}`, `/fx/{pair}`, `/anomalies`). Since your current code is Flask and pandas, the lowest-friction path is **FastAPI** reusing the same logic. Django is the better choice only if you want its admin panel for content editing.
5. **Frontend:** Next.js App Router with ISR. Pages are prebuilt and revalidated (for example every 5 minutes for FX, daily for stocks), so they are fast and cheap while data stays fresh.
6. **Edge:** Cloudflare in front for caching, DDoS protection, and free analytics.

## 3. Recommended tools

- **Frontend:** Next.js, TypeScript, Tailwind, `next-intl` (EN/FR/AR with RTL support)
- **Charts:** TradingView Lightweight Charts (free, fast, looks professional) for price charts; Recharts or ECharts for simpler visuals
- **Backend:** FastAPI + SQLAlchemy, Pydantic for validation
- **Jobs:** Celery + Redis, or simply GitHub Actions cron / systemd timers to start
- **DB:** PostgreSQL 16 + TimescaleDB (Timescale Cloud, Neon, or self-hosted)
- **Hosting (cheap start):** Vercel or Cloudflare Pages for Next.js; a small VPS (Hetzner or similar, a few dollars/month) for API, DB, and workers, via Docker Compose
- **Monitoring:** Sentry for errors, Uptime Kuma for scraper health, Google Search Console and GA4 for SEO
- **Data sources to evaluate:** BVMT public pages, Banque Centrale de Tunisie (official rates), free FX APIs (exchangerate.host-type services, ECB feeds), and gold or fuel sources. **Check each source's terms of use and redistribution rights before publishing**, especially for market data. Scraping an exchange's site and republishing it can be restricted. Consider attributing sources and showing delayed data.

## 4. SEO engine (what creates traffic)

- **Programmatic pages with real substance:** each stock page should have the chart, key stats, dividend history, anomaly history, and related news, not just a ticker and a number. Thin templated pages get penalized.
- **URL structure:** `/fr/bourse/tunis/attijari-bank`, `/en/currency/eur-tnd`, `/ar/...`, with `hreflang` tags between languages.
- **Technical:** auto-generated sitemaps split by section, JSON-LD structured data, canonical URLs, Core Web Vitals in the green, and internal linking (stock to sector to related stocks).
- **Freshness signals:** visible "last updated" timestamps and daily market summary pages ("Bourse de Tunis: clôture du 16 octobre").
- **Long-tail targets:** "cours EUR TND aujourd'hui", "Tunindex aujourd'hui", "dividende [company] 2026", "prix de l'or en Tunisie".

## 5. Monetization setup

- **AdSense:** needs a privacy policy, about and contact pages, and a cookie/consent banner (a Google-certified CMP is required for EEA/UK traffic). Place ads with reserved space to avoid layout shift, which hurts both Core Web Vitals and ad quality.
- **Placement:** one ad under the main chart, one in the sidebar, one in-content. Avoid cluttering the above-the-fold dashboard, because UX drives retention.
- **Add-ons:** broker and forex affiliate links (check that promoting them is legal and allowed in your target markets), and a newsletter (daily market summary) as an owned audience.
- **Later:** Ezoic or Mediavine at higher traffic; a paid API or premium alerts tier.

## 6. Phased roadmap

**Phase 0, Validation (week 1)**
Check keyword volume for 20 target queries (Google Trends, Search Console data from your existing sites, Ahrefs/Semrush free tiers). Confirm data-source terms. Pick a name and domain.

**Phase 1, MVP (weeks 2–4)**
Port your existing dataset into Postgres. Build the daily ingestion job, the stock list, 10–20 deep company pages, Tunindex page, and the EUR/USD to TND pages. Deploy with sitemap and Search Console.

**Phase 2, Differentiate (weeks 5–8)**
Launch the anomaly feed, full 60+ company coverage, FR/EN/AR, daily summary pages, newsletter signup, and apply for AdSense once you have 30+ quality pages and some indexed traffic.

**Phase 3, Scale (months 3–6)**
Add gold, fuel, and prayer-times/weather modules if they perform; calculators; comparison tools ("compare two stocks"); alerts; an English-language layer targeting higher-RPM traffic.

## 7. Risks to plan for

- **Data legality and reliability:** the biggest risk. Scrapers break when sites change, so alert on stale data. Display disclaimers: "informational only, not investment advice."
- **Low RPM from local traffic:** Tunisian traffic pays little per view. Expect modest income until you add English/European audiences or affiliate revenue. Treat early months as an SEO investment.
- **Regulation:** publishing anomaly flags about named companies needs careful wording to avoid defamation claims. Keep the "statistical outlier, not a finding of wrongdoing" framing visible.
- **Slow start:** new domains typically take months to rank. Publishing consistently and earning a few backlinks (Tunisian finance forums, university pages, your portfolio sites) helps.

## 8. Suggested next step

Start with the data layer, since it is the foundation and you already have most of it: a Postgres schema (`companies`, `prices_daily`, `anomalies`, `news_items`, `fx_rates`) and a daily ingestion job. I can write that schema and the FastAPI skeleton, or the Next.js page templates and sitemap setup, whichever you want first.