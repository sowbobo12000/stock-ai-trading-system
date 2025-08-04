from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (GammaExposure, SignalScore
)
from .serializers import GammaExposureSerializer, SignalScoreSerializer

class GammaExposureViewSet(viewsets.ModelViewSet):
    queryset = GammaExposure.objects.all()
    serializer_class = GammaExposureSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['symbol']
    ordering_fields = ['expiry_date', 'gex_value']
    ordering = ['-expiry_date']

    @swagger_auto_schema(
        method='get',
        operation_description="특정 symbol에 대한 최근 GEX 확인",
        manual_parameters=[
            openapi.Parameter('symbol', openapi.IN_QUERY, description="심볼", type=openapi.TYPE_STRING, required=True)
        ]
    )
    @action(detail=False, methods=['get'])
    def latest_by_symbol(self, request):
        symbol = request.query_params.get("symbol")
        if not symbol:
            return Response({"error": "Missing symbol"}, status=400)

        latest = GammaExposure.objects.filter(symbol=symbol).order_by('-expiry_date').first()
        if not latest:
            return Response({"message": "No data for symbol"}, status=404)

        return Response(self.get_serializer(latest).data)



class SignalScoreViewSet(viewsets.ModelViewSet):
    queryset = SignalScore.objects.all()
    serializer_class = SignalScoreSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['symbol', 'signal_type']
    ordering_fields = ['time_frame', 'score']
    ordering = ['-score']

    @action(detail=False, methods=["get"])
    def top_ranked(self, request):
        symbol = request.query_params.get("symbol")
        if not symbol:
            return Response({"error": "Missing symbol"}, status=status.HTTP_400_BAD_REQUEST)
        qs = self.queryset.filter(symbol=symbol.upper()).order_by('-score')[:5]
        return Response(self.get_serializer(qs, many=True).data)
