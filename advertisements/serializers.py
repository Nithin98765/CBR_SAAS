from rest_framework import serializers
from .models import Advertisement, AdvertisementImage

class AdvertisementImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = AdvertisementImage
        fields = ['id', 'image']
    
    
    def get_image(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url
    
class AdvertisementCreateSerializer(serializers.ModelSerializer):
    
    state = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    locality = serializers.CharField(required=True)
    pincode = serializers.CharField(required=True)
    contact_name = serializers.CharField(required=True)
    contact_mobile = serializers.CharField(required=True)
    
    attributes = serializers.JSONField(required=False)
    
    
    class Meta:
        model = Advertisement
        fields = [
            'id',
            'title',
            'description',
            'price',
            'negotiable',
            'state',
            'city',
            'locality',
            'pincode',
            'contact_name',
            'contact_mobile',
            'attributes'
        ]
        
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value
    
    def validate_pincode(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Pincode must be a 6-digit number.")
        return value    
    
    def validate_contact_mobile(self, value):
        if not value.startswith('+') or not value[1:].isdigit():
            raise serializers.ValidationError("Contact mobile must be in international format, e.g. +919876543210.")
        return value
    
    def validate_attributes(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Attributes must be a JSON object.")
        return value
    
    
    
class AdvertisemetListSerializer(serializers.ModelSerializer):
    images = AdvertisementImageSerializer(many=True, read_only=True)
    
    image = serializers.SerializerMethodField()
    
    seller_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Advertisement
        fields = [
            'id',
            'title',
            'description',
            'price',
            'negotiable',
            'state',
            'city',
            'locality',
            'pincode',
            'contact_name',
            'contact_mobile',
            'attributes',
            'images',
            'image',  # Add the image field here
            'seller_name'
            'created_at',
            'updated_at'
        ]
    def get_image(self, obj):
        first_image = obj.images.first()
        if not first_image or not first_image.image:
            return None
        
        request = self.context.get('request')
        image_url = first_image.image.url
        if request:
            return request.build_absolute_uri(image_url)
        
        return image_url
    
    
