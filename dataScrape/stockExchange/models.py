from django.db import models

class Company(models.Model):
    companyName=models.CharField(max_length=200,null=True,blank=True)
    emailAddress=models.CharField(max_length=200,null=True,blank=True,unique=False)
    sector=models.CharField(max_length=200,null=True,blank=True)
    symbol=models.CharField(max_length=200,null=True,blank=True)
    contactNumber=models.IntegerField(null=True,blank=True,)
    _id=models.IntegerField(primary_key=True,editable=True)

    def __str__(self):
        return (self.companyName)
    
class priceHistory(models.Model):
    company=models.ForeignKey(Company,on_delete=models.CASCADE)
    date=models.DateField(null=True)
    openPrice=models.DecimalField(max_digits=100,decimal_places=2,null=True,blank=True)
    highPrice=models.DecimalField(max_digits=100,decimal_places=2,null=True,blank=True)
    lowPrice=models.DecimalField(max_digits=100,decimal_places=2,null=True,blank=True)
    closePrice=models.DecimalField(max_digits=100,decimal_places=2,null=True,blank=True)
    volumeTraded=models.DecimalField(max_digits=100,decimal_places=2,null=True,blank=True)
    
    def __str__(self):
        return (self.date)




