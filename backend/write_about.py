path = 'e:/projects/MONEY GENERATOR APPS/live-data-dashboard-adsense/frontend/app/[lang]/about/page.tsx'
content = '''import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { locales } from '@/lib/i18n';
import Header from '@/components/Header/Header';
import Footer from '@/components/Footer/Footer';
import SEO from '@/components/SEO/SEO';
import messagesEn from '@/messages/en.json';
import messagesFr from '@/messages/fr.json';
import messagesAr from '@/messages/ar.json';

const messagesMap: Record<string, any> = {
  en: messagesEn,
  fr: messagesFr,
  ar: messagesAr,
};

interface AboutPageProps {
  params: Promise<{ lang: string }>;
}

export async function generateStaticParams() {
  return locales.map((lang) => ({ lang }));
}

export async function generateMetadata({ params }: AboutPageProps): Promise<Metadata> {
  return {
    title: 'About - Tunisia Markets Hub',
    description: 'About Tunisia Markets Hub',
  };
}

export default async function AboutPage({ params }: AboutPageProps) {
  const { lang } = await params;
  const messages = messagesMap[lang];
  const t = messages.common;
  const tNav = messages.nav;

  if (!locales.includes(lang as 'en' | 'fr' | 'ar')) {
    notFound();
  }

  return (
    <div className="space-y-8">
      <SEO
        title={tNav('about_page')}
        description="About Tunisia Markets Hub - your source for real-time Tunisian financial market data"
        path={`/${lang}/about`}
        locale={lang}
      />

      <section className="bg-muted/50 rounded-xl p-8 md:p-12">
        <h1 className="text-3xl font-bold mb-4">{tNav('about_page')}</h1>
        <p className="text-lg text-muted-foreground mb-6">
          Tunisia Markets Hub is a Tunisia-first financial markets platform providing real-time
          BVMT stock prices, FX rates, commodity prices, and AI-powered anomaly detection.
        </p>
        <p className="text-muted-foreground">
          Our mission is to make Tunisian financial market data accessible, transparent, and
          easy to understand for investors, researchers, and anyone interested in the MENA region\'s
          markets.
        </p>
      </section>

      <section className="space-y-6">
        <h2 className="text-2xl font-bold">Our Data Sources</h2>
        <ul className="space-y-3 text-muted-foreground max-w-xl">
          <li className="flex items-center gap-3">
            <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs">1</span>
            BVMT (Bourse de Tunis) - Stock prices and market data
          </li>
          <li className="flex items-center gap-3">
            <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs">2</span>
            Banque Centrale de Tunisie (BCT) - Official FX rates
          </li>
          <li className="flex items-center gap-3">
            <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs">3</span>
            ECB and free FX APIs - Currency rates
          </li>
          <li className="flex items-center gap-3">
            <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs">4</span>
            Various sources - Commodity prices (gold, fuel, etc.)
          </li>
        </ul>
      </section>

      <section className="bg-muted/50 rounded-xl p-8 md:p-12">
        <h2 className="text-2xl font-bold mb-4">Disclaimer</h2>
        <p className="text-muted-foreground max-w-2xl">
          Data provided for informational purposes only. Not investment advice. Always consult
          with a qualified financial advisor before making investment decisions. Market data may
          be delayed. We do not guarantee the accuracy or completeness of the information provided.
        </p>
      </section>
    </div>
  );
}
'''
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('About page written successfully')