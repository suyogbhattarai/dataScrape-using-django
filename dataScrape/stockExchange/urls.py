from django.urls import path
from .views import   *

urlpatterns =[

    path('company/<str:symbol>/', getCompany, name="company"),
    path('company/',getCompanies,name="companies"),
    path('scrape/',scrapeDate,name="scrape"),
    path('company/delete/<str:pk>',deleteCompany,name="companyDelete")
  


]