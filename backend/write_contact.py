path = 'e:/projects/MONEY GENERATOR APPS/live-data-dashboard-adsense/frontend/app/[lang]/contact/page.tsx'
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

interface ContactPageProps {
  params: Promise<{ lang: string }>;
}

export async function generateStaticParams() {
  return locales.map((lang) => ({ lang }));
}

export async function generateMetadata({ params }: ContactPageProps): Promise<Metadata> {
  return {
    title: 'Contact - Tunisia Markets Hub',
    description: 'Contact Tunisia Markets Hub',
  };
}

export default async function ContactPage({ params }: ContactPageProps) {
  const { lang } = await params;
  const messages = messagesMap[lang];
  const tNav = messages.nav;

  if (!locales.includes(lang as 'en' | 'fr' | 'ar')) {
    notFound();
  }

  return (
    <div className="space-y-8">
      <SEO
        title={tNav('contact')}
        description="Contact Tunisia Markets Hub"
        path={`/${lang}/contact`}
        locale={lang}
      />

      <section className="bg-muted/50 rounded-xl p-8 md:p-12 max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">{tNav('contact')}</h1>
        <div className="space-y-6">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl shrink-0">
              ✉️
            </div>
            <div>
              <h3 className="font-semibold">Email</h3>
              <p className="text-muted-foreground">contact@tunisia-markets.com</p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl shrink-0">
              📍
            </div>
            <div>
              <h3 className="font-semibold">Address</h3>
              <p className="text-muted-foreground">Tunis, Tunisia</p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl shrink-0">
              🌐
            </div>
            <div>
              <h3 className="font-semibold">Website</h3>
              <p className="text-muted-foreground">https://tunisia-markets.com</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
'''
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Contact page written successfully')