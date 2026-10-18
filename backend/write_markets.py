path = 'e:/projects/MONEY GENERATOR APPS/live-data-dashboard-adsense/frontend/app/[lang]/markets/page.tsx'
content = r'''import type { Metadata } from 'next';
import { useTranslations } from 'next-intl';
import { getTranslations } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { locales } from '@/lib/i18n';
import Header from '@/components/Header/Header';
import Footer from '@/components/Footer/Footer';
import SEO from '@/components/SEO/SEO';
import { generateSEOMetadata } from '@/components/SEO/SEO';
import MarketSummary from '@/components/MarketSummary/MarketSummary';
import AdBanner from '@/components/AdBanner/AdBanner';
import Link from 'next/link';
import { apiClient } from '@/lib/api-client';
import type { Company } from '@/types/api';

interface MarketsPageProps {
  params: Promise<{ lang: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export async function generateStaticParams() {
  return locales.map((lang) => ({ lang }));
}

export async function generateMetadata({ params }: MarketsPageProps): Promise<Metadata> {
  const { lang } = await params;
  const t = await getTranslations({ locale: lang, namespace: 'seo' });
  return generateSEOMetadata(t('marketData'), t('defaultDescription'), `/${lang}/markets`, lang);
}

export default async function MarketsPage({ params, searchParams }: MarketsPageProps) {
  const { lang } = await params;
  const { sector, limit = '50', page = '1' } = await searchParams;
  const t = useTranslations('market');
  const tNav = useTranslations('nav');

  if (!locales.includes(lang as 'en' | 'fr' | 'ar')) {
    notFound();
  }

  let companies: Company[] = [];
  let isLoading = false;
  let total = 0;

  try {
    const response = await apiClient.getCompanies({
      sector: sector as string,
      limit: parseInt(limit as string),
      skip: (parseInt(page as string) - 1) * parseInt(limit as string),
    });
    companies = response.data || [];
    total = response.meta?.total || companies.length;
  } catch {
    isLoading = true;
  }

  const marketData = companies.map((c) => ({
    symbol: c.ticker,
    name: c[`name_${lang}` as keyof Company] || c.name_en,
    price: 0, change: 0, changePercent: 0, volume: 0,
    open: 0, high: 0, low: 0, close: 0, previousClose: 0,
    sector: c.sector_name_en || c.sector_name_fr || '',
    currency: 'TND' as const,
  }));

  return (
    <div className="space-y-8">
      <SEO title={tNav('bourse')} description="BVMT stock prices" path={`/${lang}/markets`} locale={lang} />
      <AdBanner format="leaderboard" className="mb-6" />
      <MarketSummary title={t('title')} subtitle={t('subtitle')} data={marketData} isLoading={isLoading} showAds={false} />
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">{tNav('bourse')}</h2>
        <div className="flex gap-2">
          <Link href={`/${lang}/markets?sector=BANKS`} className="px-3 py-1 border rounded text-sm">Banks</Link>
          <Link href={`/${lang}/markets?sector=INDUSTRIALS`} className="px-3 py-1 border rounded text-sm">Industrials</Link>
          <Link href={`/${lang}/markets?sector=CONSUMER_GOODS`} className="px-3 py-1 border rounded text-sm">Consumer</Link>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead><tr className="border-b bg-muted/50">
            <th className="pb-3 text-left text-sm font-medium text-muted-foreground">Ticker</th>
            <th className="pb-3 text-left text-sm font-medium text-muted-foreground">Company</th>
            <th className="pb-3 text-left text-sm font-medium text-muted-foreground">Sector</th>
            <th className="pb-3 text-right text-sm font-medium text-muted-foreground">Price (TND)</th>
            <th className="pb-3 text-right text-sm font-medium text-muted-foreground">Change %</th>
            <th className="pb-3 text-right text-sm font-medium text-muted-foreground">Volume</th>
          </tr></thead>
          <tbody>
            {companies.map((c) => {
              const latest = c.last_price ?? 0;
              const changePct = c.daily_change_pct ?? 0;
              return (
                <tr key={c.id} className="border-b hover:bg-muted/30 transition-colors">
                  <td className="py-4"><Link href={`/${lang}/markets/${c.ticker.toLowerCase()}`} className="font-medium text-primary hover:underline">{c.ticker}</Link></td>
                  <td className="py-4">{c[`name_${lang}` as keyof Company] || c.name_en}</td>
                  <td className="py-4 text-muted-foreground text-sm">{c.sector_name_en || c.sector_name_fr || '-'}</td>
                  <td className="py-4 text-right font-mono">{latest.toFixed(3)}</td>
                  <td className="py-4 text-right"><span className={`font-medium ${changePct >= 0 ? 'text-green-500' : 'text-red-500'}`}>{changePct >= 0 ? '+' : ''}{changePct.toFixed(2)}%</span></td>
                  <td className="py-4 text-right text-muted-foreground">-</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {total > parseInt(limit as string) && (
        <div className="flex items-center justify-between pt-4">
          <div className="text-sm text-muted-foreground">Showing {companies.length} of {total} companies</div>
        </div>
      )}
    </div>
  );
}
'''
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Markets page written')
path = 'e:/projects/MONEY GENERATOR APPS/live-data-dashboard-adsense/frontend/app/[lang]/markets/page.tsx'
content = r'''import type { Metadata } from 'next';
import { useTranslations } from 'next-intl';
import { getTranslations } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { locales } from '@/lib/i18n';
import Header from '@/components/Header/Header';
import Footer from '@/components/Footer/Footer';
import SEO from '@/components/SEO/SEO';
import { generateSEOMetadata } from '@/components/SEO/SEO';
import MarketSummary from '@/components/MarketSummary/MarketSummary';
import AdBanner from '@/components/AdBanner/AdBanner';
import Link from 'next/link';
import { apiClient } from '@/lib/api-client';
import type { Company } from '@/types/api';

interface MarketsPageProps {
  params: Promise<{ lang: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export async function generateStaticParams() {
  return locales.map((lang) => ({ lang }));
}

export async function generateMetadata({ params }: MarketsPageProps): Promise<Metadata> {
  const { lang } = await params;
  const t = await getTranslations({ locale: lang, namespace: 'seo' });
  return generateSEOMetadata(t('marketData'), t('defaultDescription'), `/${lang}/markets`, lang);
}

export default async function MarketsPage({ params, searchParams }: MarketsPageProps) {
  const { lang } = await params;
  const { sector, limit = '50', page = '1' } = await searchParams;
  const t = useTranslations('market');
  const tNav = useTranslations('nav');

  if (!locales.includes(lang as 'en' | 'fr' | 'ar')) {
    notFound();
  }

  let companies: Company[] = [];
  let isLoading = false;
  let total = 0;

  try {
    const response = await apiClient.getCompanies({
      sector: sector as string,
      limit: parseInt(limit as string),
      skip: (parseInt(page as string) - 1) * parseInt(limit as string),
    });
    companies = response.data || [];
    total = response.meta?.total || companies.length;
  } catch {
    isLoading = true;
  }

  const marketData = companies.map((c) => ({
    symbol: c.ticker,
    name: c[`name_${lang}` as keyof Company] || c.name_en,
    price: 0, change: 0, changePercent: 0, volume: 0,
    open: 0, high: 0, low: 0, close: 0, previousClose: 0,
    sector: c.sector_name_en || c.sector_name_fr || '',
    currency: 'TND' as const,
  }));

  return (
    <div className="space-y-8">
      <SEO title={tNav('bourse')} description="BVMT stock prices" path={`/${lang}/markets`} locale={lang} />
      <AdBanner format="leaderboard" className="mb-6" />
      <MarketSummary title={t('title')} subtitle={t('subtitle')} data={marketData} isLoading={isLoading} showAds={false} />
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">{tNav('bourse')}</h2>
        <div className="flex gap-2">
          <Link href={`/${lang}/markets?sector=BANKS`} className="px-3 py-1 border rounded text-sm">Banks</Link>
          <Link href={`/${lang}/markets?sector=INDUSTRIALS`} className="px-3 py-1 border rounded text-sm">Industrials</Link>
          <Link href={`/${lang}/markets?sector=CONSUMER_GOODS`} className="px-3 py-1 border rounded text-sm">Consumer</Link>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead><tr className="border-b bg-muted/50">
            <th className="pb-3 text-left text-sm font-medium text-muted-foreground">Ticker</th>
            <th className="pb-3 text-left text-sm font-medium text-muted-foreground">Company</th>
            <th className="pb-3 text-left text-sm font-medium text-muted-foreground">Sector</th>
            <th className="pb-3 text-right text-sm font-medium text-muted-foreground">Price (TND)</th>
            <th className="pb-3 text-right text-sm font-medium text-muted-foreground">Change %</th>
            <th className="pb-3 text-right text-sm font-medium text-muted-foreground">Volume</th>
          </tr></thead>
          <tbody>
            {companies.map((c) => {
              const latest = c.last_price ?? 0;
              const changePct = c.daily_change_pct ?? 0;
              return (
                <tr key={c.id} className="border-b hover:bg-muted/30 transition-colors">
                  <td className="py-4"><Link href={`/${lang}/markets/${c.ticker.toLowerCase()}`} className="font-medium text-primary hover:underline">{c.ticker}</Link></td>
                  <td className="py-4">{c[`name_${lang}` as keyof Company] || c.name_en}</td>
                  <td className="py-4 text-muted-foreground text-sm">{c.sector_name_en || c.sector_name_fr || '-'}</td>
                  <td className="py-4 text-right font-mono">{latest.toFixed(3)}</td>
                  <td className="py-4 text-right"><span className={`font-medium ${changePct >= 0 ? 'text-green-500' : 'text-red-500'}`}>{changePct >= 0 ? '+' : ''}{changePct.toFixed(2)}%</span></td>
                  <td className="py-4 text-right text-muted-foreground">-</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {total > parseInt(limit as string) && (
        <div className="flex items-center justify-between pt-4">
          <div className="text-sm text-muted-foreground">Showing {companies.length} of {total} companies</div>
        </div>
      )}
    </div>
  );
}
'''
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Markets page written')
path = 'e:/projects/MONEY GENERATOR APPS/live-data-dashboard-adsense/frontend/app/[lang]/markets/page.tsx'
content = r'''import type { Metadata } from 'next';
import { useTranslations } from 'next-intl';
import { getTranslations } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { locales } from '@/lib/i18n';
import Header from '@/components/Header/Header';
import Footer from '@/components/Footer/Footer';
import SEO from '@/components/SEO/SEO';
import { generateSEOMetadata } from '@/components/SEO/SEO';
import MarketSummary from '@/components/MarketSummary/MarketSummary';
import AdBanner from '@/components/AdBanner/AdBanner';
import Link from 'next/link';
import { apiClient } from '@/lib/api-client';
import type { Company } from '@/types/api';

interface MarketsPageProps {
  params: Promise<{ lang: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export async function generateStaticParams() {
  return locales.map((lang) => ({ lang }));
}

export async function generateMetadata({ params }: MarketsPageProps): Promise<Metadata> {
  const { lang } = await params;
  const t = await getTranslations({ locale: lang, namespace: 'seo' });
  return generateSEOMetadata(t('marketData'), t('defaultDescription'), `/${lang}/markets`, lang);
}

export default async function MarketsPage({ params, searchParams }: MarketsPageProps) {
  const { lang } = await params;
  const { sector, limit = '50', page = '1' } = await searchParams;
  const t = useTranslations('market');
  const tNav = useTranslations('nav');

  if (!locales.includes(lang as 'en' | 'fr' | 'ar')) {
    notFound();
  }

  let companies: Company[] = [];
  let isLoading = false;
  let total = 0;

  try {
    const response = await apiClient.getCompanies({
      sector: sector as string,
      limit: parseInt(limit as string),
      skip: (parseInt(page as string) - 1) * parseInt(limit as string),
    });
    companies = response.data || [];
    total = response.meta?.total || companies.length;
  } catch {
    isLoading = true;
  }

  const marketData = companies.map((c) => ({
    symbol: c.ticker,
    name: c[`name_${lang}` as keyof Company] || c.name_en,
    price: 0, change: 0, changePercent: 0, volume: 0,
    open: 0, high: 0, low: 0, close: 0, previousClose: 0,
    sector: c.sector_name_en || c.sector_name_fr || '',
    currency: 'TND' as const,
  }));

  return (
    <div className="space-y-8">
      <SEO title={tNav('bourse')} description="BVMT stock prices" path={`/${lang}/markets`} locale={lang} />
      <AdBanner format="leaderboard" className="mb-6" />
      <MarketSummary title={t('title')} subtitle={t('subtitle')} data={marketData} isLoading={isLoading} showAds={false} />
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">{tNav('bourse')}</h2>
        <div className="flex gap-2">
          <Link href={`/${lang}/markets?sector=BANKS`} className="px-3 py-1 border rounded text-sm">Banks</Link>
          <Link href={`/${lang}/markets?sector=INDUSTRIALS`} className="px-3 py-1 border rounded text-sm">Industrials</Link>
          <Link href={`/${lang}/markets?sector=CONSUMER_GOODS`} className="px-3 py-1 border rounded text-sm">Consumer</Link>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead><tr className="border-b bg-muted/50">
            <th className="pb-3 text-left text-sm font-medium text-muted-foreground">Ticker</th>
            <th className="pb-3 text-left text-sm font-medium text-muted-foreground">Company</th>
            <th className="pb-3 text-left text-sm font-medium text-muted-foreground">Sector</th>
            <th className="pb-3 text-right text-sm font-medium text-muted-foreground">Price (TND)</th>
            <th className="pb-3 text-right text-sm font-medium text-muted-foreground">Change %</th>
            <th className="pb-3 text-right text-sm font-medium text-muted-foreground">Volume</th>
          </tr></thead>
          <tbody>
            {companies.map((c) => {
              const latest = c.last_price ?? 0;
              const changePct = c.daily_change_pct ?? 0;
              return (
                <tr key={c.id} className="border-b hover:bg-muted/30 transition-colors">
                  <td className="py-4"><Link href={`/${lang}/markets/${c.ticker.toLowerCase()}`} className="font-medium text-primary hover:underline">{c.ticker}</Link></td>
                  <td className="py-4">{c[`name_${lang}` as keyof Company] || c.name_en}</td>
                  <td className="py-4 text-muted-foreground text-sm">{c.sector_name_en || c.sector_name_fr || '-'}</td>
                  <td className="py-4 text-right font-mono">{latest.toFixed(3)}</td>
                  <td className="py-4 text-right"><span className={`font-medium ${changePct >= 0 ? 'text-green-500' : 'text-red-500'}`}>{changePct >= 0 ? '+' : ''}{changePct.toFixed(2)}%</span></td>
                  <td className="py-4 text-right text-muted-foreground">-</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {total > parseInt(limit as string) && (
        <div className="flex items-center justify-between pt-4">
          <div className="text-sm text-muted-foreground">Showing {companies.length} of {total} companies</div>
        </div>
      )}
    </div>
  );
}
'''
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Markets page written')
import sys  
\"path = 'e:/projects/MONEY GENERATOR APPS/live-data-dashboard-adsense/frontend/app/[lang]/markets/page.tsx'\"  
\"content = '''import type { Metadata } from 'next';\"  
\"import { useTranslations } from 'next-intl';\"  
\"import { getTranslations } from 'next-intl/server';\"  
\"import { notFound } from 'next/navigation';\"  
\"import { locales } from '@/lib/i18n';\"  
\"import Header from '@/components/Header/Header';\"  
\"import Footer from '@/components/Footer/Footer';\"  
\"import SEO from '@/components/SEO/SEO';\"  
\"import { generateSEOMetadata } from '@/components/SEO/SEO';\"  
\"import MarketSummary from '@/components/MarketSummary/MarketSummary';\"  
\"import AdBanner from '@/components/AdBanner/AdBanner';\"  
\"import Link from 'next/link';\"  
\"import { apiClient } from '@/lib/api-client';\"  
\"import type { Company } from '@/types/api';\" 
\"\"  
\"interface MarketsPageProps {\"  
\"  params: Promise<{ lang: string }>;\"  
\"  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;\"  
\"}\"  
\"\"  
\"export async function generateStaticParams() {\"  
\"  return locales.map((lang) => ({ lang }));\"  
\"}\"  
\"\"  
\"export async function generateMetadata({ params }: MarketsPageProps): Promise<Metadata> {\"  
\"  const { lang } = await params;\"  
\"  const t = await getTranslations({ locale: lang, namespace: 'seo' });\"  
\"  return generateSEOMetadata(t('marketData'), t('defaultDescription'), \`/${lang}/markets\`, lang);\"  
\"\"  
\"export default async function MarketsPage({ params, searchParams }: MarketsPageProps) {\"  
\"  const { lang } = await params;\"  
\"  const { sector, limit = '50', page = '1' } = await searchParams;\"  
\"  const t = useTranslations('market');\"  
\"  const tNav = useTranslations('nav');\"  
\"\"  
\"  if (!locales.includes(lang as 'en' | 'fr' | 'ar')) {\"  
\"    notFound();\"  
\"  }\"  
\"\"  
\"  let companies: Company[] = [];\"  
\"  let isLoading = false;\"  
\"  let total = 0;\"  
\"\"  
\"  try {\"  
\"    const response = await apiClient.getCompanies({\"  
\"      sector: sector as string,\"  
\"      limit: parseInt(limit as string),\"  
\"      skip: (parseInt(page as string) - 1) * parseInt(limit as string),\"  
\"    });\"  
\"    companies = response.data || [];\"  
\"    total = response.meta?.total || companies.length;\"  
\"  } catch {\"  
\"    isLoading = true;\"  
\"\"  
\"  const marketData = companies.map((c) => ({\"  
\"    symbol: c.ticker,\"  
\"    name: c[\`name_\${lang}\` as keyof Company] || c.name_en,\"  
\"    price: 0, change: 0, changePercent: 0, volume: 0,\"  
\"    open: 0, high: 0, low: 0, close: 0, previousClose: 0,\"  
\"    sector: c.sector_name_en || c.sector_name_fr || '',\"  
\"    currency: 'TND' as const,\"  
\"  }));\"  
\"\"  
\"  return (\"  
\"    <div className=\\\"space-y-8\\\">\"  
\"      <SEO title={tNav('bourse')} description=\\\"BVMT stock prices\\\" path={\`/${lang}/markets\`} locale={lang} />\"  
\"\"  
\"      <AdBanner format=\\\"leaderboard\\\" className=\\\"mb-6\\\" />\"  
\"\"  
\"      <MarketSummary title={t('title')} subtitle={t('subtitle')} data={marketData} isLoading={isLoading} showAds={false} />\"  
\"\"  
\"      <div className=\\\"flex items-center justify-between mb-4\\\">\"  
\"        <h2 className=\\\"text-2xl font-bold\\\">{tNav('bourse')}</h2>\"  
\"        <div className=\\\"flex gap-2\\\">\"  
\"          <Link href={\`/${lang}/markets?sector=BANKS\`} className=\\\"px-3 py-1 border rounded text-sm\\\">Banks</Link>\"  
\"          <Link href={\`/${lang}/markets?sector=INDUSTRIALS\`} className=\\\"px-3 py-1 border rounded text-sm\\\">Industrials</Link>\"  
\"          <Link href={\`/${lang}/markets?sector=CONSUMER_GOODS\`} className=\\\"px-3 py-1 border rounded text-sm\\\">Consumer</Link>\"  
\"        </div>\"  
\"\"  
\"      <div className=\\\"overflow-x-auto\\\">\"  
\"        <table className=\\\"w-full text-left border-collapse\\\">\"  
\"          <thead><tr className=\\\"border-b bg-muted/50\\\">\"  
\"            <th className=\\\"pb-3 text-left text-sm font-medium text-muted-foreground\\\">Ticker</th>\"  
\"            <th className=\\\"pb-3 text-left text-sm font-medium text-muted-foreground\\\">Company</th>\"  
\"            <th className=\\\"pb-3 text-left text-sm font-medium text-muted-foreground\\\">Sector</th>\"  
\"            <th className=\\\"pb-3 text-right text-sm font-medium text-muted-foreground\\\">Price (TND)</th>\"  
\"            <th className=\\\"pb-3 text-right text-sm font-medium text-muted-foreground\\\">Change %</th>\"  
\"            <th className=\\\"pb-3 text-right text-sm font-medium text-muted-foreground\\\">Volume</th>\"  
\"          </tr></thead>\"  
\"          <tbody>\"  
\"            {companies.map((c) => {\"  
\"              const latest = c.last_price ?? 0;\"  
\"              const changePct = c.daily_change_pct ?? 0;\"  
\"              return (\"  
\"                <tr key={c.id} className=\\\"border-b hover:bg-muted/30 transition-colors\\\">\"  
\"                  <td className=\\\"py-4\\\"><Link href={\`/${lang}/markets/${c.ticker.toLowerCase()}\`} className=\\\"font-medium text-primary hover:underline\\\">{c.ticker}</Link></td>\"  
\"                  <td className=\\\"py-4\\\">{c[\`name_\${lang}\` as keyof Company] || c.name_en}</td>\"  
\"                  <td className=\\\"py-4 text-muted-foreground text-sm\\\">{c.sector_name_en || c.sector_name_fr || '-'}</td>\"  
\"                  <td className=\\\"py-4 text-right font-mono\\\">{latest.toFixed(3)}</td>\"  
\"                  <td className=\\\"py-4 text-right\\\"><span className={\`font-medium \${changePct >= 0 ? 'text-green-500' : 'text-red-500'}\`}>{changePct >= 0 ? '+' : ''}{changePct.toFixed(2)}%</span></td>\"  
\"                  <td className=\\\"py-4 text-right text-muted-foreground\\\">-</td>\"  
\"                </tr>\"  
\"              );\"  
\"            })}\"  
\"          </tbody>\"  
\"        </table>\"  
\"      </div>\"  
\"\"  
\"      {total > parseInt(limit as string) && (\"  
\"        <div className=\\\"flex items-center justify-between pt-4\\\">\"  
\"          <div className=\\\"text-sm text-muted-foreground\\\">Showing {companies.length} of {total} companies</div>\"  
\"        </div>\"  
\"      )}\"  
\"\"  
\"    </div>\"  
\"  );\"  
\"}\"  
\"'''\"  
\"with open(path, 'w', encoding='utf-8') as f:\"  
\"    f.write(content)\"  
