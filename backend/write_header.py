path = 'e:/projects/MONEY GENERATOR APPS/live-data-dashboard-adsense/frontend/components/Header/Header.tsx'
content = '''// components/Header/Header.tsx
"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import LanguageSwitcher from '@/components/LanguageSwitcher/LanguageSwitcher';
import messagesEn from '@/messages/en.json';
import messagesFr from '@/messages/fr.json';
import messagesAr from '@/messages/ar.json';

const messagesMap: Record<string, any> = {
  en: messagesEn,
  fr: messagesFr,
  ar: messagesAr,
};

const Header = () => {
  const pathname = usePathname();

  // Extract locale from pathname
  const localeMatch = pathname.match(/^\\/(en|fr|ar)/);
  const currentLocale = localeMatch ? localeMatch[1] : 'en';

  const messages = messagesMap[currentLocale];
  const t = (key: string) => messages.nav?.[key] || key;

  const navLinks = [
    { key: 'home', href: `/${currentLocale}` },
    { key: 'markets', href: `/${currentLocale}/markets` },
    { key: 'anomalies', href: `/${currentLocale}/anomalies` },
    { key: 'news', href: `/${currentLocale}/news` },
    { key: 'about', href: `/${currentLocale}/about` },
  ];

  const isActive = (href: string) => {
    return pathname === href;
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between">
        <Link href={`/${currentLocale}`} className="flex items-center space-x-2">
          <div className="flex-shrink-0">
            <span className="text-xl font-bold text-primary">Tunisia Markets</span>
          </div>
        </Link>

        <nav className="hidden md:flex items-center space-x-2">
          {navLinks.map((link) => (
            <Link
              key={link.key}
              href={link.href}
              className={`
                px-4 py-2 text-sm font-medium rounded-md transition-colors
                ${isActive(link.href)
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                }
              `}
            >
              {t(link.key)}
            </Link>
          ))}
        </nav>

        <div className="flex items-center space-x-4">
          <LanguageSwitcher />
          <button
            aria-label="Menu"
            className="md:hidden p-2 rounded-md text-foreground hover:bg-accent"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
'''
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Header written successfully')