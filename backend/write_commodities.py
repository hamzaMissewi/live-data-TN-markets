path = 'e:/projects/MONEY GENERATOR APPS/live-data-dashboard-adsense/frontend/app/[lang]/commodities/page.tsx'
content = '''use client;

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { usePathname } from 'next/navigation';
import Header from '@/components/Header/Header';
import Footer from '@/components/Footer/Footer';
import SEO from '@/components/SEO/SEO';
import AdBanner from '@/components/AdBanner/AdBanner';
import Link from 'next/link';
import { apiClient } from '@/lib/api-client';
import type { CommodityPrice } from '@/types/api';

export default function CommoditiesPage({ params }: { params: { lang: string } }) {
  const { lang } = params;
  const t = useTranslations('commodities');
  const tNav = useTranslations('nav');
  const pathname = usePathname();

  const localeMatch = pathname.match(/^\\/(en|fr|ar)/);
  const currentLocale = localeMatch ? localeMatch[1] : 'en';

  const [commodities, setCommodities] = useState<CommodityPrice[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    apiClient.getCommodityPrices()
      .then(data => {
        setCommodities(data);
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      <SEO
        title={t('title')}
        description="Gold, oil, and commodity prices in Tunisia"
        path={pathname}
        locale={currentLocale}
      />

      <AdBanner format="leaderboard" className="mb-6" />

      <section className="bg-card border rounded-xl p-6">
        <h1 className="text-2xl font-bold mb-6">{t('title')}</h1>
        <p className="text-muted-foreground mb-6">
          Latest prices for gold, silver, oil, and other commodities with local unit conversions.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {commodities.map((c) => (
            <div key={c.id} className="bg-muted/50 rounded-lg p-4">
              <Link
                href={`/${currentLocale}/commodities/${c.code.toLowerCase()}`}
                className="block"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{c.name}</span>
                  <span className="text-xs text-muted-foreground">{c.code}</span>
                </div>
                <div className="text-lg font-mono font-bold">
                  {(0).toFixed(2)}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {c.unit}
                </div>
              </Link>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
'''
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Commodities page written successfully')