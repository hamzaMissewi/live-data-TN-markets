"""BVMT (Bourse de Tunis) scraper module."""
from datetime import date
from decimal import Decimal
import httpx
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class BVMTScraper:
    """Scraper for Bourse de Tunis (BVMT) data."""
    
    BASE_URL = settings.BVMT_BASE_URL
    
    def __init__(self, client=None):
        self.client = client or httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=settings.SCRAPER_TIMEOUT,
            headers={"User-Agent": settings.SCRAPER_USER_AGENT},
        )
    
    async def get_company_list(self) -> List[Dict[str, Any]]:
        """Fetch list of all listed companies."""
        url = f"{self.BASE_URL}/fr/actions/listed-companies"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find("table", {"class": "companies-table"})
            companies = []
            if table:
                for row in table.find_all("tr")[1:]:
                    cells = row.find_all("td")
                    if len(cells) >= 4:
                        companies.append({
                            "ticker": cells[0].get_text(strip=True),
                            "name_en": cells[1].get_text(strip=True),
                            "name_fr": cells[1].get_text(strip=True),
                            "name_ar": cells[1].get_text(strip=True),
                            "sector": cells[2].get_text(strip=True),
                            "price": cells[3].get_text(strip=True),
                        })
            return companies
        except Exception as e:
            logger.error(f"Failed to fetch company list: {e}")
            return []
    
    async def get_company_history(self, ticker: str, days: int = 365) -> List[Dict[str, Any]]:
        """Fetch historical prices for a company."""
        url = f"{self.BASE_URL}/fr/actions/{ticker}/historique"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find("table", {"class": "history-table"})
            prices = []
            if table:
                for row in table.find_all("tr")[1:]:
                    cells = row.find_all("td")
                    if len(cells) >= 6:
                        prices.append({
                            "date": self._parse_date(cells[0].get_text(strip=True)),
                            "open": self._parse_price(cells[1].get_text(strip=True)),
                            "high": self._parse_price(cells[2].get_text(strip=True)),
                            "low": self._parse_price(cells[3].get_text(strip=True)),
                            "close": self._parse_price(cells[4].get_text(strip=True)),
                            "volume": self._parse_volume(cells[5].get_text(strip=True)),
                        })
            return prices[-days:] if len(prices) > days else prices
        except Exception as e:
            logger.error(f"Failed to fetch history for {ticker}: {e}")
            return []
    async def get_current_prices(self) -> Dict[str, Dict[str, Any]]:
        """Fetch current day prices for all companies."""
        url = f"{self.BASE_URL}/fr/marches"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find("table", {"class": "live-prices"})
            prices = {}
            if table:
                for row in table.find_all("tr")[1:]:
                    cells = row.find_all("td")
                    if len(cells) >= 5:
                        ticker = cells[0].get_text(strip=True)
                        prices[ticker] = {
                            "price": self._parse_price(cells[1].get_text(strip=True)),
                            "change": self._parse_change(cells[2].get_text(strip=True)),
                            "volume": self._parse_volume(cells[3].get_text(strip=True)),
                            "turnover": self._parse_price(cells[4].get_text(strip=True)),
                        }
            return prices
        except Exception as e:
            logger.error(f"Failed to fetch current prices: {e}")
            return {}
    
    async def get_sector_data(self) -> List[Dict[str, Any]]:
        """Fetch sector performance data."""
        url = f"{self.BASE_URL}/fr/marches/par-sector"
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            sectors = []
            for sector_elem in soup.find_all("div", {"class": "sector-item"}):
                name_elem = sector_elem.find("h3")
                perf_elem = sector_elem.find("span", {"class": "performance"})
                if name_elem and perf_elem:
                    sectors.append({
                        "name": name_elem.get_text(strip=True),
                        "performance": self._parse_change(perf_elem.get_text(strip=True)),
                    })
            return sectors
        except Exception as e:
            logger.error(f"Failed to fetch sector data: {e}")
            return []
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        from dateutil import parser
        try:
            return parser.parse(date_str, dayfirst=True).date()
        except Exception:
            return None
    
    def _parse_price(self, price_str: str) -> Optional[Decimal]:
        try:
            cleaned = price_str.replace("TND", "").replace(" ", "").replace(",", ".")
            return Decimal(cleaned)
        except Exception:
            return None
    
    def _parse_volume(self, volume_str: str) -> int:
        try:
            cleaned = volume_str.replace(" ", "").replace(",", "")
            return int(cleaned) if cleaned else 0
        except Exception:
            return 0
    
    def _parse_change(self, change_str: str) -> Optional[float]:
        try:
            cleaned = change_str.replace("%", "").strip()
            return float(cleaned)
        except Exception:
            return None