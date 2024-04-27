import logging

import requests
from django.db import DatabaseError
from django.http import JsonResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from requests.exceptions import RequestException
from rest_framework import filters
from rest_framework import serializers
from rest_framework import viewsets

from .models import Product
from .models import ProductUnit
from .models import Qr  # , WarehouseViewSet
from .models import Transfer  # , WarehouseViewSet
from .models import Wh

logger = logging.getLogger(__name__)


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
        return JsonResponse({"message": "No new data to post or update."})
    except ValueError:
        logger.exception("Value error encountered")
        return JsonResponse({"error": "Invalid input provided"}, status=400)
    except DatabaseError:
        logger.exception("Database error encountered")
        return JsonResponse({"error": "Problem accessing the database"}, status=500)
    except Exception:  # As a last resort
        logger.exception("Unexpected error occurred")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)


def fetch_data_from_my_api():
    url = "http://192.168.100.50:8000/products/"
    headers = {
        "Authorization": "Token e60c85b3f42fdd2c3f4d9ecb394b99d532f312f1",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return {item["name"]: item for item in response.json()}


def fetch_data_from_external_api():
    url = "https://mysupplier.mozzn.com/products/?page_size=999"
    headers = {
        "Authorization": "SUPP eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5MzA1MTYzLCJpYXQiOjE3MDc3NjkxNjMsImp0aSI6IjM5YzdmYzVlMmQ2YTQ1MGRiZTYwZjIxNmIwZTViMjljIiwidXNlcl9pZCI6MTJ9.-P2ZPwdyUkImvm34_RWi-fB3Pjk_rFGzKAc7Ywg8uSo",  # noqa: E501
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Raises an exception for HTTP error responses
    return response.json()["results"]


def prepare_data_for_post(my_data, external_data):
    new_data = []
    patch_data = []

    for item in external_data:
        if item["name"] in my_data:
            existing_item = my_data[item["name"]]
            if (
                item["is_active"] != existing_item["is_active"]
                or item["category"] != existing_item["category"]
            ):
                patch_data.append(
                    {
                        "id": existing_item[
                            "id"
                        ],  # Assume we have 'id' in existing_item
                        "is_active": item["is_active"],
                        "category": item["category"],
                    },
                )
        else:
            new_data.append(
                {
                    "name": item["name"],
                    "is_active": item["is_active"],
                    "category": item["category"],
                },
            )

    return new_data, patch_data


def post_data_to_my_api(prepared_data):
    url = "http://192.168.100.50:8000/products/"
    headers = {
        "Authorization": "Token e60c85b3f42fdd2c3f4d9ecb394b99d532f312f1",
        "Content-Type": "application/json",
    }
    for product in prepared_data:
        response = requests.post(url, json=product, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an exception for HTTP error responses


def patch_data_to_my_api(patch_data):
    url_template = (
        "http://192.168.100.50:8000/products/{id}/"  # Ensure URL is correct for PATCH
    )
    headers = {
        "Authorization": "Token e60c85b3f42fdd2c3f4d9ecb394b99d532f312f1",
        "Content-Type": "application/json",
    }

    for product in patch_data:
        product_url = url_template.format(id=product["id"])
        response = requests.patch(
            product_url,
            json=product,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()


class QrSerializer(serializers.ModelSerializer):
    # Use PrimaryKeyRelatedField or SlugRelatedField for writable foreign keys
    wh = serializers.PrimaryKeyRelatedField(queryset=Wh.objects.all())

    class Meta:
        model = Qr
        fields = ["id", "wh", "productunit", "quantity", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def to_representation(self, instance):
        """Modify the output of certain fields for serialization"""
        representation = super().to_representation(instance)
        representation["wh"] = (
            f"{instance.wh.name} - {instance.wh.Smacc_Code}"  # Custom output for wh
        )
        representation["productunit"] = f"{instance.productunit.ProductUnit_name}"

        return representation


class WhSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wh
        fields = "__all__"


class WhViewSet(viewsets.ModelViewSet):
    queryset = Wh.objects.all()
    serializer_class = WhSerializer


class QrViewSet(viewsets.ModelViewSet):
    queryset = Qr.objects.all()
    serializer_class = QrSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["wh__name", "wh__Smacc_Code"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "is_active", "category"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter products by name",
                required=False,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        """
        Optionally restricts the products returned by name,
        using a 'name' query parameter.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get("name", None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ["id", "From", "To", "quantity"]


class TransferViewSet(viewsets.ModelViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer


class ProductUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductUnit
        fields = "__all__"


class ProductUnitViewSet(viewsets.ModelViewSet):
    queryset = ProductUnit.objects.all()
    serializer_class = ProductUnitSerializer


# Product_unit API
def refresh_api_unit(request):
    try:
        my_data = (
            fetch_data_from_my_unit()
        )  # This needs to correspondingly fetch Product_Unit objects
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
        return JsonResponse(
            {"error": "Network or HTTP error occurred: " + str(e)},
            status=502,
        )
    except KeyError as e:
        return JsonResponse(
            {"error": "Data format error - missing key: " + str(e)},
            status=500,
        )
    except ValueError:
        logger.exception("Value error encountered")
        return JsonResponse({"error": "Invalid input provided"}, status=400)


def fetch_data_from_my_unit():  # Fetch data from my API
    url = "http://192.168.100.50:8000/productunits/"
    headers = {
        "Authorization": "Token e60c85b3f42fdd2c3f4d9ecb394b99d532f312f1",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return {item["product_unit_name"]: item for item in response.json()}


def fetch_data_from_unit():  # Fetch data from external API
    url = "https://mysupplier.mozzn.com/products/units/?page_size=9999"
    headers = {
        "Authorization": "SUPP eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5MzA1MTYzLCJpYXQiOjE3MDc3NjkxNjMsImp0aSI6IjM5YzdmYzVlMmQ2YTQ1MGRiZTYwZjIxNmIwZTViMjljIiwidXNlcl9pZCI6MTJ9.-P2ZPwdyUkImvm34_RWi-fB3Pjk_rFGzKAc7Ywg8uSo",  # noqa: E501
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    # Remove 'created_by' from each item in 'results'
    for item in data["results"]:
        if "created_by" in item:
            del item["created_by"]
    return data["results"]


def prepare_data_for_post_unit(my_data, external_data):  # Prepare data for POST/PATCH
    new_data = []
    patch_data = []

    for item in external_data:
        try:
            if item["product_unit_name"] in my_data:
                existing_item = my_data[item["product_unit_name"]]
                if item["is_active"] != existing_item["is_active"]:
                    patch_data.append(item)
            else:
                new_data.append(item)
        except ValueError:
            logger.exception("Value error encountered")
            return JsonResponse({"error": "Invalid input provided"}, status=400)

    return new_data, patch_data


def post_data_to_my_api_unit(new_data):  # POST
    url = "http://192.168.100.50:8000/productunits/"
    headers = {
        "Authorization": "Token e60c85b3f42fdd2c3f4d9ecb394b99d532f312f1",
        "Content-Type": "application/json",
    }
    for product_unit in new_data:
        try:
            response = requests.post(
                url,
                json=product_unit,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()  # unsuccessful status codes

        except requests.exceptions.HTTPError:
            logger.exception("Failed to create product unit: %s", response.status_code)
            try:
                # Attempt to log JSON error message if it exists
                logger.exception("Error message: %s", response.json())
            except ValueError:
                # If response is not in JSON format, log the raw response text
                logger.exception("Error response: %s", response.text)
        except requests.exceptions.RequestException:
            logger.exception("A requests exception occurred")


def patch_data_to_my_api_unit(patch_data):  # PATCH
    url_template = "http://192.168.100.50:8000/productunits/{id}/"
    headers = {
        "Authorization": "Token e60c85b3f42fdd2c3f4d9ecb394b99d532f312f1",
        "Content-Type": "application/json",
    }
    for product_unit in patch_data:
        product_url = url_template.format(id=product_unit["id"])
        response = requests.patch(
            product_url,
            json=product_unit,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
