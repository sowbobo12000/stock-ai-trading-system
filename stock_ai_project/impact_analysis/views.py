from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import NewsImpact, SignalScore
from .serializers import NewsImpactSerializer


class NewsImpactViewSet(viewsets.ModelViewSet):
    """
    API endpoint for retrieving and managing AI-generated news impact analysis results.
    """
    queryset = NewsImpact.objects.select_related("news").all()
    serializer_class = NewsImpactSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['news__symbol', 'sentiment', 'impact_type']
    ordering_fields = ['score', 'risk_score', 'analysis_time']
    ordering = ['-analysis_time']

    @swagger_auto_schema(
        operation_description="Retrieve all impact results related to a given stock symbol.",
        manual_parameters=[
            openapi.Parameter(
                'symbol', openapi.IN_QUERY,
                description="Stock symbol (e.g., TSLA)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="List of news impacts for the given symbol",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_OBJECT)
                )
            ),
            400: "Missing symbol parameter"
        }
    )
    @action(detail=False, methods=["get"], url_path="by-symbol")
    def by_symbol(self, request):
        symbol = request.query_params.get("symbol")
        if not symbol:
            return Response({"error": "Missing symbol"}, status=status.HTTP_400_BAD_REQUEST)

        impacts = self.queryset.filter(news__symbol=symbol.upper()).order_by('-analysis_time')
        serializer = self.get_serializer(impacts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete all impact analysis records for a given symbol.",
        manual_parameters=[
            openapi.Parameter(
                'symbol', openapi.IN_QUERY,
                description="Stock symbol to delete (e.g., AAPL)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: "Deleted", 404: "No impacts found"}
    )
    @action(detail=False, methods=["delete"], url_path="delete-by-symbol")
    def delete_by_symbol(self, request):
        symbol = request.query_params.get("symbol")
        if not symbol:
            return Response({"error": "Missing symbol"}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = self.queryset.filter(news__symbol=symbol.upper()).delete()
        if deleted == 0:
            return Response({"message": "No impacts found for this symbol"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": f"Deleted {deleted} records for {symbol.upper()}"}, status=status.HTTP_200_OK)





class LLMFeedbackViewSet(viewsets.ModelViewSet):
    queryset = LLMFeedback.objects.all()
    serializer_class = LLMFeedbackSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def submit(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({"message": "Feedback submitted."}, status=status.HTTP_201_CREATED)


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['symbol', 'alert_type']
    ordering_fields = ['created_at', 'score']
    ordering = ['-created_at']

    @action(detail=False, methods=["get"])
    def recent(self, request):
        symbol = request.query_params.get("symbol")
        if not symbol:
            return Response({"error": "Missing symbol"}, status=status.HTTP_400_BAD_REQUEST)
        alerts = self.queryset.filter(symbol=symbol.upper())[:10]
        return Response(self.get_serializer(alerts, many=True).data)


