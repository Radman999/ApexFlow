from rest_framework import serializers, viewsets
from .models import qr, Transfer#, WarehouseViewSet
from .models import wh, productunit, product, product_unit
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.http import HttpResponse
import subprocess
import requests
from django.shortcuts import render
from django.http import JsonResponse
from requests.exceptions import RequestException
def refresh_api(request):
    try:
        my_data = fetch_data_from_my_api()
        external_data = fetch_data_from_external_api()
        new_data, patch_data = prepare_data_for_post(my_data, external_data)
        
        if new_data:
            post_data_to_my_api(new_data)
        if patch_data:
            patch_data_to_my_api(patch_data)
        
        if new_data or patch_data:
            return JsonResponse({"message": "API refreshed successfully!"})
        else:
            return JsonResponse({"message": "No new data to post or update."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def fetch_data_from_my_api():
    url = "http://192.168.100.50:8000/products/"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    existing_data = {item['name']: item for item in response.json()}  # Creating a dictionary of existing items by name
    return existing_data



def fetch_data_from_external_api():
    url = "https://mysupplier.mozzn.com/products/?page_size=999"
    headers = {"Authorization": "SUPP eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5MzA1MTYzLCJpYXQiOjE3MDc3NjkxNjMsImp0aSI6IjM5YzdmYzVlMmQ2YTQ1MGRiZTYwZjIxNmIwZTViMjljIiwidXNlcl9pZCI6MTJ9.-P2ZPwdyUkImvm34_RWi-fB3Pjk_rFGzKAc7Ywg8uSo",
            "Content-Type": "application/json"
            }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an exception for HTTP error responses
    return response.json()['results']

def prepare_data_for_post(my_data, external_data):
    new_data = []
    patch_data = []
    
    for item in external_data:
        if item['name'] in my_data:
            existing_item = my_data[item['name']]
            if item['is_active'] != existing_item['is_active'] or item['category'] != existing_item['category']:
                patch_data.append({
                    'id': existing_item['id'],  # Assume we have 'id' in existing_item
                    'is_active': item['is_active'],
                    'category': item['category']
                })
        else:
            new_data.append({
                'name': item['name'],
                'is_active': item['is_active'],
                'category': item['category']
            })

    return new_data, patch_data

def post_data_to_my_api(prepared_data):
    url = "http://192.168.100.50:8000/products/"
    headers = {"Content-Type": "application/json"}
    for product in prepared_data:
        response = requests.post(url, json=product, headers=headers)
        response.raise_for_status()  # Raises an exception for HTTP error responses
        print("Product created:", response.json())


def patch_data_to_my_api(patch_data):
    url_template = "http://192.168.100.50:8000/products/{id}/"  # Ensure URL is correct for PATCH
    headers = {
        "Content-Type": "application/json"}
    
    for product in patch_data:
        product_url = url_template.format(id=product['id'])
        response = requests.patch(product_url, json=product, headers=headers)
        response.raise_for_status()
        print("Product updated:", response.json())



class qrSerializer(serializers.ModelSerializer):
    # Use PrimaryKeyRelatedField or SlugRelatedField for writable foreign keys
    wh = serializers.PrimaryKeyRelatedField(queryset=wh.objects.all())
    class Meta:
        model = qr
        fields = ['id', 'wh', 'productunit', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        """ Modify the output of certain fields for serialization """
        representation = super().to_representation(instance)
        representation['wh'] = f"{instance.wh.name} - {instance.wh.Smacc_Code}"  # Custom output for wh

        return representation
class qrViewSet(viewsets.ModelViewSet):
    queryset = qr.objects.all()
    serializer_class = qrSerializer



class productSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = product
        fields = ['id', 'name', 'is_active','category']

class productViewSet(viewsets.ModelViewSet):
    queryset = product.objects.all()
    serializer_class = productSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter products by name',
                required=False
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        Optionally restricts the products returned by name,
        using a 'name' query parameter.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset
        


class TransferSerializer(serializers.ModelSerializer):
    From = serializers.PrimaryKeyRelatedField(queryset=qr.objects.all())
    To = serializers.PrimaryKeyRelatedField(queryset=wh.objects.all())
    class Meta:
        model = Transfer
        fields = ['id', 'From', 'To', 'quantity']
    
    def to_representation(self, instance):
        """ Modify the output of certain fields for serialization """
        representation = super().to_representation(instance)
        representation['From'] = f"{instance.From.wh.name} - {instance.From.productunit.product.name} - {instance.From.productunit.unit.name} - {instance.From.productunit.unit_frac.name}"
        representation['To'] = f"{instance.To.name} - {instance.To.Smacc_Code}"
        return representation
class TransferViewSet(viewsets.ModelViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer

class product_unitSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = product_unit
        fields = '__all__'

class product_unitViewSet(viewsets.ModelViewSet):
    queryset = product_unit.objects.all()
    serializer_class = product_unitSerializer







# Product_unit API 
def refresh_api_unit(request):
    try:
        my_data = fetch_data_from_my_unit()  # This needs to correspondingly fetch Product_Unit objects
        external_data = fetch_data_from_unit()
        new_data, patch_data = prepare_data_for_post_unit(my_data, external_data)
        
        if new_data:
            post_data_to_my_api_unit(new_data)
        if patch_data:
            patch_data_to_my_api_unit(patch_data)
        if new_data:
            return JsonResponse({"message": "API Unit created successfully!"})
        if patch_data:
            return JsonResponse({"message": "API refreshed successfully!"})
        if not new_data and not patch_data:
            return JsonResponse({"message": "No new data to post or update."})
    except RequestException as e:
        return JsonResponse({"error": "Network or HTTP error occurred: " + str(e)}, status=502)
    except KeyError as e:
        return JsonResponse({"error": "Data format error - missing key: " + str(e)}, status=500)
    except Exception as e:
        return JsonResponse({"error": "An unexpected error occurred: " + str(e)}, status=500)
    


def fetch_data_from_my_unit(): #Fetch data from my API
    url = "http://192.168.100.50:8000/productunits/"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print("API response:", response.text)  # Add this line to debug the actual API response
    existing_data = {item['product_unit_name']: item for item in response.json()}  # Creating a dictionary of existing items by name
    return existing_data




def fetch_data_from_unit(): #Fetch data from external API
    url = "https://mysupplier.mozzn.com/products/units/?page_size=9999"  
    headers = {"Authorization": "SUPP eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5MzA1MTYzLCJpYXQiOjE3MDc3NjkxNjMsImp0aSI6IjM5YzdmYzVlMmQ2YTQ1MGRiZTYwZjIxNmIwZTViMjljIiwidXNlcl9pZCI6MTJ9.-P2ZPwdyUkImvm34_RWi-fB3Pjk_rFGzKAc7Ywg8uSo",
            "Content-Type": "application/json"
            }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    # Remove 'created_by' from each item in 'results'
    for item in data['results']:
        if 'created_by' in item:
            del item['created_by']
    print("API response:", data)  # Add this line to debug the actual API response
    return data['results']



def prepare_data_for_post_unit(my_data, external_data): #Prepare data for POST/PATCH
    new_data = []
    patch_data = []
    print("test")

    for item in external_data:
        print("test inside item")
        try:
            if item['product_unit_name'] in my_data:
                existing_item = my_data[item['product_unit_name']]
                if item['is_active'] != existing_item['is_active']:
                    patch_data.append(item)
            else:
                new_data.append(item)
        except TypeError as e:
            print(f"Error processing item {item}: {str(e)}")  # Log any errors in item processing
            continue

    return new_data, patch_data

    

def post_data_to_my_api_unit(new_data): #POST
    url = "http://192.168.100.50:8000/productunits/"
    headers = {"Content-Type": "application/json"}
    for product_unit in new_data:
        response = requests.post(url, json=product_unit, headers=headers)
        response.raise_for_status()
        print("Product unit created:", response.json())



def patch_data_to_my_api_unit(patch_data): #PATCH
    url_template = "http://192.168.100.50:8000/productunits/{id}/"
    headers = {"Content-Type": "application/json"}
    for product_unit in patch_data:
        product_url = url_template.format(id=product_unit['id'])
        response = requests.patch(product_url, json=product_unit, headers=headers)
        response.raise_for_status()
        print("Product unit updated:", response.json())