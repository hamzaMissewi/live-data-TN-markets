path = 'e:/projects/MONEY GENERATOR APPS/live-data-dashboard-adsense/frontend/app/[lang]/news/page.tsx'
content = '''import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { locales } from '@/lib/i18n';
import Header from '@/components/Header/Header';
import Footer from '@/components/Footer/Footer';
import SEO from '@/components/SEO/SEO';
import AdBanner from '@/components/AdBanner/AdBanner';
import NewsCard from '@/components/NewsCard/NewsCard';
import { apiClient } from '@/lib/api-client';
import messagesEn from '@/messages/en.json';
import messagesFr from '@/messages/fr.json';
import messagesAr from '@/messages/ar.json';

const messagesMap: Record<string, any> = {
  en: messagesEn,
  fr: messagesFr,
  ar: messagesAr,
};

type LangParams = { lang: string };

interface NewsPageProps {
  params: Promise<LangParams>;
  searchParams?: any;
}

export async function generateStaticParams() {
  return locales.map((lang) => ({ lang }));
}

export async function generateMetadata({ params }: NewsPageProps): Promise<Metadata> {
  return {
    title: 'News - Tunisia Markets Hub',
    description: 'Latest market news and financial articles',
  };
}

export default async function NewsPage({ params, searchParams }: NewsPageProps) {
  const { lang } = await params;
  const { ticker } = await searchParams;
  const messages = messagesMap[lang];
  const t = messages.news;
  const tNav = messages.nav;

  if (!locales.includes(lang as 'en' | 'fr' | 'ar')) {
    notFound();
  }

  let news: any[] = [];
  let isLoading = false;

  try {
    news = await apiClient.getNews({
      limit: 50,
      ticker: ticker as string,
    });
  } catch {
    isLoading = true;
  }

  return (
    <div className="space-y-8">
      <SEO
        title={t('title')}
        description="Latest market news and financial articles"
        path={`/${lang}/news`}
        locale={lang}
      />

      <AdBanner format="leaderboard" className="mb-6" />

      <section className="bg-card border rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold">{t('title')}</h1>
            <p className="text-muted-foreground">
              Latest financial news from Tunisian and international sources.
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {news.length > 0 ? (
            news.map((n) => (
              <NewsCard key={n.id} news={n} locale={lang} compact={false} />
            ))
          ) : (
            <p className="text-sm text-muted-foreground text-center py-8">
              No news available
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
'''
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('News page written successfully')