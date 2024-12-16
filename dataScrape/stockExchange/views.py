from django.http import HttpResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date
from rest_framework.response import  Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .models import *
from .serializers import * 
from bs4 import BeautifulSoup
from datetime import datetime
from rest_framework import status  
import requests


@api_view(['GET'])
def getPriceHistory(request):
    company_name = request.query_params.get('company', None)
    start_date = request.query_params.get('start-date', None)
    end_date = request.query_params.get('end-date', None)

    price_history_queryset = priceHistory.objects.all()

    if company_name:
        price_history_queryset = price_history_queryset.filter(company__companyName__iexact=company_name)

    if start_date:
            start_date = parse_date(start_date)
            if start_date:
                price_history_queryset = price_history_queryset.filter(date__gte=start_date)

    if end_date:
            end_date = parse_date(end_date)
            if end_date:
                price_history_queryset = price_history_queryset.filter(date__lte=end_date)

      
    serializer = priceHistorySerializer(price_history_queryset, many=True)


    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def getCompanies(request):
    companies=Company.objects.all()
    serializer= companySerializer(companies,many=True)    
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def getCompany(request, symbol):


    try:
      
        company = Company.objects.get(symbol__iexact=symbol)  
    except Company.DoesNotExist:
        return Response({"error": "Company not found"}, status=404)

   
    serializer = companySerializer(company, many=False)    
    
  
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])  
def updateCompany(request, pk):
    try:
        company = Company.objects.get(_id=pk)
    except Company.DoesNotExist:
        return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data

  
    if 'companyName' in data:
        company.companyName = data['companyName']
    if 'emailAddress' in data:
        company.emailAddress = data['emailAddress']
    if 'sector' in data:
        company.sector = data['sector']
    if 'symbol' in data:
        company.symbol = data['symbol']
    if 'contactNumber' in data:
        company.contactNumber = data['contactNumber']

    # Save the updated company data
    company.save()

    # Serialize the updated company data
    serializer = companySerializer(company, many=False)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])  
def deleteCompany(request, pk):
    try:
       
        company = Company.objects.get(_id=pk)
    except Company.DoesNotExist:
        return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)


    company.delete()

 
    return Response({"message": "Company deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

def scrapeDate(request):
    base_url = "https://nepalstock.com.np/company/detail/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    companies = Company.objects.all()

    for company in companies:
        url = f"{base_url}{company.pk}"  
        print(f"Scraping data for {company.companyName} from {url}...")
        
        try:
            response = requests.get(url, headers=headers)  
            if response.status_code != 200:
                print(f"Failed to retrieve data for {company.companyName}. Status code: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", {"class": "table"})

            if not table:
                print(f"No table found for {company.companyName}.")
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
                        volume_traded = float(cols[6].text.strip().replace(",", "")) if len(cols) > 6 else 0

                        try:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                        except ValueError:
                            print(f"Invalid date format for {company.companyName} on {date_str}. Skipping row.")
                            continue

                        
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
                        print(f"Saved price history for {company.companyName} on {date_obj}.")

                    except Exception as e:
                        print(f"Error processing row for {company.companyName}: {e}")

        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")

    print("Scraping completed.")
    base_url = "https://nepalstock.com.np/company/detail/"
    headers = {'User-Agent': 'Mozilla/5.0'}

    
    companies = Company.objects.all()

    for company in companies:
        url = f"{base_url}{company._id}"
        print(f"Scraping data for {company.companyName} from {url}...")
        response = request.get(url, headers=headers)
        return HttpResponse(f"Failed to retrieve data for {company.companyName}.")

        if response.status_code != 200:
            return HttpResponse(f"Failed to retrieve data for {company.companyName}.")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"class": "table"})

        if not table:
            print(f"No table found for {company.companyName}.")
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
                    print(
                        f"Saved price history for {company.companyName} on {date_obj}."
                    )

                except Exception as e:
                    print(f"Error processing row: {e}")

    return HttpResponse("Success")


