from rest_framework import serializers, viewsets
from .models import qr, Transfer#, WarehouseViewSet
from .models import wh, productunit
class qrSerializer(serializers.ModelSerializer):
    # Use PrimaryKeyRelatedField or SlugRelatedField for writable foreign keys
    wh = serializers.PrimaryKeyRelatedField(queryset=wh.objects.all())
    productunit = serializers.PrimaryKeyRelatedField(queryset=productunit.objects.all())
    class Meta:
        model = qr
        fields = ['id', 'wh', 'productunit', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        """ Modify the output of certain fields for serialization """
        representation = super().to_representation(instance)
        representation['wh'] = f"{instance.wh.name} - {instance.wh.Smacc_Code}"  # Custom output for wh
        # Custom output for productunit, including multiple related fields for detail
        representation['productunit'] = f"{instance.productunit.product.name} - {instance.productunit.unit.name} - {instance.productunit.unit_frac.name}"
        representation['created_at'] = instance.created_at.strftime('%Y-%m-%d %H:%M:%S')
        representation['updated_at'] = instance.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        return representation





    # def get_wh(self, obj):
    #     return obj.wh.name
    # def get_productunit(self, obj):
    #     return obj.productunit.product.name + ' - ' + obj.productunit.unit.name + ' - ' + obj.productunit.unit_frac.name
    # def get_created_at(self, obj):
    #     return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    # def get_updated_at(self, obj):
    #     return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
class qrViewSet(viewsets.ModelViewSet):
    queryset = qr.objects.all()
    serializer_class = qrSerializer

#class WarehouseSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = warehouse
#        fields = ['id', 'name', 'quantity']
#class WarehouseViewSet(viewsets.ModelViewSet):
#    queryset = warehouse.objects.all()
#    serializer_class = WarehouseSerializer

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