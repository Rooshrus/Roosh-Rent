from rest_framework import serializers
from .models import Room

class RoomSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    image_url = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    bookings_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Room
        fields = "__all__"

    def get_image_url(self, obj):
        request = self.context.get("request")
        url = obj.image_url
        if request is not None and url and url.startswith("/"):
            return request.build_absolute_uri(url)
        return url

    def get_images(self, obj):
        request = self.context.get("request")
        out = []
        for img in obj.images.all().order_by("uploaded_at"):
            url = img.image.url
            if request is not None and url.startswith("/"):
                out.append(request.build_absolute_uri(url))
            else:
                out.append(url)
        return out
