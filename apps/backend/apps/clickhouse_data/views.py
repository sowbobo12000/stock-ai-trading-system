from rest_framework import viewsets
from .models import OptionData, OHLCData, NewsData
from .serializers import OptionDataSerializer, OHLCDataSerializer, NewsDataSerializer

class OptionDataViewSet(viewsets.ModelViewSet):
    queryset = OptionData.objects.all()
    serializer_class = OptionDataSerializer

class OHLCDataViewSet(viewsets.ModelViewSet):
    queryset = OHLCData.objects.all()
    serializer_class = OHLCDataSerializer

class NewsDataViewSet(viewsets.ModelViewSet):
    queryset = NewsData.objects.all()
    serializer_class = NewsDataSerializer
