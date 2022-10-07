from datetime import datetime, timedelta

from rest_framework import generics, status
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Item
from . import serializers

@api_view(['GET'])
def ApiOverview(request):
    api_urls = {
        'Imports': '/imports',
        'Delete': '/delete/<str:id>',
        'Node': '/nodes/<str:id>'
    }
    return Response(api_urls)

class ImportsView(generics.CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = serializers.ImportsSerializer

    def create(self, request, *args, **kwargs):
        updateDate = request.data.get('updateDate')
        for item in request.data['items']:
            item['date'] = updateDate
        response = super().create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response

class DeleteView(generics.DestroyAPIView):
    queryset = Item.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        date = request.query_params.get('date')
        if date is None:
            raise ValidationError('date parameter is required')
        response = super().destroy(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response
