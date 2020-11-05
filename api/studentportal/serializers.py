from api.generic.serializers import ResourceModelSerializer
from assignments.models import Resource

class StudentPortalResourceModelSerializer(ResourceModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'
        ordering = ['-id', ]
