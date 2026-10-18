path = 'e:/projects/MONEY GENERATOR APPS/live-data-dashboard-adsense/frontend/app/[lang]/currencies/[pair]/page.tsx'
content = '''import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { locales } from '@/lib/i18n';
import SEO from '@/components/SEO/SEO';
import AdBanner from '@/components/AdBanner/AdBanner';
import Link from 'next/link';
import { apiClient } from '@/lib/api-client';
import messagesEn from '@/messages/en.json';
import messagesFr from '@/messages/fr.json';
import messagesAr from '@/messages/ar.json';

const messagesMap: Record<string, any> = {
  en: messagesEn,
  fr: messagesFr,
  ar: messagesAr,
};

interface FXDetailPageProps {
  params: Promise<{ lang: string; pair: string }>;
}

export async function generateStaticParams() {
  const pairs = ['eurtnd', 'usdtnd', 'gbptnd', 'chtnd', 'tndeur', 'tndusd'];
  return locales.flatMap((lang) =>
    pairs.map((pair) => ({ lang, pair }))
  );
}

export async function generateMetadata({ params }: FXDetailPageProps): Promise<Metadata> {
  const { lang, pair } = await params;
  const messages = messagesMap[lang];
  const seo = messages.seo;

  return {
    title: `${pair.toUpperCase()} - ${seo?.defaultTitle || 'Tunisia Markets Hub'}`,
    description: `${pair.toUpperCase()} exchange rate history`,
  };
}

export default async function FXDetailPage({ params }: FXDetailPageProps) {
  const { lang, pair } = await params;
  const messages = messagesMap[lang];
  const t = (key: string) => messages.fx?.[key] || key;
  const tNav = (key: string) => messages.nav?.[key] || key;

  if (!locales.includes(lang as 'en' | 'fr' | 'ar')) {
    notFound();
  }

  const pairSymbol = pair.toUpperCase();
  let history: any[] = [];

  try {
    const response = await apiClient.getFxHistory(pairSymbol, 90);
    history = response || [];
  } catch {
    // handle error
  }

  return (
    <div className="space-y-8">
      <SEO
        title={pairSymbol}
        description={`${pairSymbol} exchange rate history and chart`}
        path={`/${lang}/currencies/${pair}`}
        locale={lang}
      />

      <AdBanner format="leaderboard" className="mb-6" />

      <section className="bg-card border rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <Link href={`/${lang}/currencies`} className="text-sm text-muted-foreground hover:text-primary">
              ← {tNav('currencies')}
            </Link>
            <h1 className="text-3xl font-bold mt-1">{pairSymbol}</h1>
            <p className="text-muted-foreground">
              {pairSymbol.includes('TND') && pairSymbol.startsWith('EUR')
                ? 'Euro to Tunisian Dinar exchange rate'
                : pairSymbol.includes('TND') && pairSymbol.startsWith('USD')
                  ? 'US Dollar to Tunisian Dinar exchange rate'
                  : 'Currency exchange rate'}
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold font-mono">
              {history.length > 0 ? history[history.length - 1]?.rate?.toFixed(4) || 'N/A' : 'N/A'}
            </div>
            <div className="text-sm text-muted-foreground">TND</div>
          </div>
        </div>

        <div className="bg-muted/50 rounded-lg p-4">
          <h3 className="text-sm font-semibold mb-3">{t('rateHistory')}</h3>
          <div className="h-64 w-full">
            {history.length > 0 ? (
              <div className="text-muted-foreground text-sm">
                Chart data available for {history.length} data points
              </div>
            ) : (
              <div className="text-muted-foreground text-sm">No data available</div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
'''
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('FX detail page written successfully')