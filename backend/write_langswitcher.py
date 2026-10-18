path = 'e:/projects/MONEY GENERATOR APPS/live-data-dashboard-adsense/frontend/components/LanguageSwitcher/LanguageSwitcher.tsx'
content = '''// components/LanguageSwitcher/LanguageSwitcher.tsx
"use client";

import { usePathname, useRouter } from 'next/navigation';
import { locales, type Locale } from '@/lib/i18n';
import { isRtl } from '@/lib/i18n';

interface LanguageSwitcherProps {
  className?: string;
}

const LanguageSwitcher = ({ className = '' }: LanguageSwitcherProps) => {
  const router = useRouter();
  const pathname = usePathname();

  // Extract current locale from pathname
  const localeMatch = pathname.match(/^\\/(en|fr|ar)/);
  const [locale] = localeMatch ? localeMatch : ['en'];

  // Extract current path without locale prefix
  const getCurrentPathWithoutLocale = () => {
    const segments = pathname.split('/');
    return segments.slice(2).join('/') || '';
  };

  const switchLanguage = (newLocale: Locale) => {
    const pathWithoutLocale = getCurrentPathWithoutLocale();
    const newPath = `/${newLocale}/${pathWithoutLocale}`;

    // Set cookie for next locale
    document.cookie = `next-locale=${newLocale}; path=/; max-age=31536000`;

    router.push(newPath);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>, newLocale: Locale) => {
    if (e.key === 'Enter' || e.key === ' ') {
      switchLanguage(newLocale);
    }
  };

  return (
    <div className={`flex gap-2 ${className}`}>
      {locales.map((lang) => (
        <button
          key={lang}
          onClick={() => switchLanguage(lang)}
          onKeyDown={(e) => handleKeyDown(e, lang)}
          disabled={lang === locale}
          className={`
            px-3 py-1 text-sm font-medium rounded-md transition-all
            ${lang === locale
              ? 'bg-primary text-primary-foreground shadow-md cursor-default'
              : 'bg-muted text-muted-foreground hover:bg-accent hover:text-accent-foreground'
            }
            ${isRtl(lang) ? 'rtl:' : ''}
          `}
          aria-label={`Switch to ${lang.toUpperCase()}`}
          aria-current={lang === locale ? 'page' : undefined}
        >
          {lang.toUpperCase()}
        </button>
      ))}
    </div>
  );
};

export default LanguageSwitcher;
'''
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('LanguageSwitcher written successfully')