

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from .models import Company, priceHistory
from datetime import datetime

class Command(BaseCommand):
    help = 'Scrapes price history for all companies stored in the database'

    def handle(self, *args, **kwargs):
        base_url = "https://nepalstock.com.np/company/detail/"
        headers = {'User-Agent': 'Mozilla/5.0'}

       
        companies = Company.objects.all()

        for company in companies:
            url = f"{base_url}{company._id}"
            self.stdout.write(f"Scraping data for {company.companyName} from {url}...")
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                self.stdout.write(f"Failed to retrieve data for {company.companyName}.")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", {"class": "table"})

            if not table:
                self.stdout.write(f"No table found for {company.companyName}.")
                continue

           
            for row in table.find_all("tr")[1:]:  
                cols = row.find_all("td")
                if len(cols) >= 6:
                    try:
                       
                        date_str = cols[1].text.strip()
                        open_price = float(cols[2].text.strip().replace(",", ""))
                        high_price = float(cols[3].text.strip().replace(",", ""))
                        low_price = float(cols[4].text.strip().replace(",", ""))
                        close_price = float(cols[5].text.strip().replace(",", ""))
                        volume_traded = float(cols[6].text.strip().replace(",", ""))

                     
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

                        
                        priceHistory.objects.update_or_create(
                            company=company,
                            date=date_obj,
                            defaults={
                                "openPrice": open_price,
                                "highPrice": high_price,
                                "lowPrice": low_price,
                                "closePrice": close_price,
                                "volumeTraded": volume_traded,
                            },
                        )
                        self.stdout.write(
                            f"Saved price history for {company.companyName} on {date_obj}."
                        )

                    except Exception as e:
                        self.stdout.write(f"Error processing row: {e}")

        self.stdout.write("Scraping completed.")
