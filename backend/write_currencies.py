path = 'e:/projects/MONEY GENERATOR APPS/live-data-dashboard-adsense/frontend/app/[lang]/currencies/page.tsx'
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
import type { FXRate } from '@/types/api';

export default function CurrenciesPage({ params }: { params: { lang: string } }) {
  const { lang } = params;
  const t = useTranslations('fx');
  const tNav = useTranslations('nav');
  const pathname = usePathname();

  const localeMatch = pathname.match(/^\\/(en|fr|ar)/);
  const currentLocale = localeMatch ? localeMatch[1] : 'en';

  const [pairs, setPairs] = useState<FXRate[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    apiClient.getFxRates()
      .then(data => {
        setPairs(data);
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      <SEO
        title={t('title')}
        description="Currency exchange rates EUR/USD/GBP/CHF to TND"
        path={pathname}
        locale={currentLocale}
      />

      <AdBanner format="leaderboard" className="mb-6" />

      <section className="bg-card border rounded-xl p-6">
        <h1 className="text-2xl font-bold mb-6">{t('title')}</h1>
        <p className="text-muted-foreground mb-6">
          Latest exchange rates for major currencies against the Tunisian Dinar (TND).
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="pb-3 text-left text-sm font-medium text-muted-foreground">Pair</th>
                <th className="pb-3 text-left text-sm font-medium text-muted-foreground">Name</th>
                <th className="pb-3 text-right text-sm font-medium text-muted-foreground">Rate</th>
                <th className="pb-3 text-right text-sm font-medium text-muted-foreground">Change</th>
                <th className="pb-3 text-right text-sm font-medium text-muted-foreground">Action</th>
              </tr>
            </thead>
            <tbody>
              {pairs.map((pair) => {
                const symbol = pair.symbol.replace('/', '');
                return (
                  <tr key={pair.id} className="border-b hover:bg-muted/30 transition-colors">
                    <td className="py-4 font-mono">{pair.symbol}</td>
                    <td className="py-4">{pair.symbol}</td>
                    <td className="py-4 text-right font-mono">
                      {pair.rate?.toFixed(4) || '0.0000'}
                    </td>
                    <td className="py-4 text-right text-muted-foreground">
                      <span className="text-green-500">+0.00%</span>
                    </td>
                    <td className="py-4">
                      <Link
                        href={`/${currentLocale}/currencies/${symbol.toLowerCase()}`}
                        className="text-primary text-sm hover:underline"
                      >
                        {t('rateHistory')}
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section className="bg-muted/50 rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">{t('convert')}</h2>
        <p className="text-muted-foreground">
          Use our currency converter to calculate amounts between TND and major currencies.
        </p>
        <Link
          href={`/${currentLocale}/currencies/convert`}
          className="inline-flex items-center gap-2 text-primary font-medium hover:underline"
        >
          Go to Converter →
        </Link>
      </section>
    </div>
  );
}
'''
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Currencies page written successfully')