import boto3
import json

from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Avg

from .models import NewsArticle, OptionData, PriceCandle
from .serializers import NewsArticleSerializer, OptionDataSerializer, PriceCandleSerializer
from impact_analysis.tasks import analyze_news_impact


# Custom pagination with page size control
class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class NewsArticleViewSet(viewsets.ModelViewSet):
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['symbol', 'title', 'content']
    ordering_fields = ['published_at', 'created_at']
    ordering = ['-published_at']

    @swagger_auto_schema(
        operation_description="Trigger LLM analysis for this news article",
        responses={200: openapi.Response("Success", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ))}
    )
    @action(detail=True, methods=["post"])
    def analyze(self, request, pk=None):
        """
        Trigger an async Celery task to analyze the news article using an LLM.
        """
        news = self.get_object()
        analyze_news_impact.delay(news.id)
        return Response({"message": "LLM analysis has been scheduled."}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Reset LLM analysis result for this article",
        responses={200: openapi.Response("Analysis result reset")}
    )
    @action(detail=True, methods=["post"])
    def reset_analysis(self, request, pk=None):
        """
        Delete existing LLM analysis result (NewsImpact) if it exists.
        """
        news = self.get_object()
        if hasattr(news, "impact"):
            news.impact.delete()
        return Response({"message": "Analysis result deleted."}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='post',
        operation_description="Trigger AWS Lambda to crawl and analyze news for a given stock symbol.",
        manual_parameters=[
            openapi.Parameter(
                'symbol', openapi.IN_QUERY, description="Stock symbol (e.g., TSLA)", required=True, type=openapi.TYPE_STRING
            )
        ],
        responses={200: openapi.Response("Lambda triggered")}
    )
    @action(detail=False, methods=["post"])
    def fetch_now(self, request):
        """
        Trigger AWS Lambda to perform crawling and LLM analysis for a given symbol.
        """
        symbol = request.query_params.get("symbol")
        if not symbol:
            return Response({"error": "Missing symbol"}, status=status.HTTP_400_BAD_REQUEST)

        lambda_client = boto3.client("lambda", region_name="us-east-1")
        payload = {"symbol": symbol.upper()}

        try:
            lambda_client.invoke(
                FunctionName="stock-crawler",  # adjust to your deployed Lambda name
                InvocationType="Event",  # async
                Payload=json.dumps(payload),
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": f"Triggered Lambda for {symbol}"}, status=status.HTTP_200_OK)


class OptionDataViewSet(viewsets.ModelViewSet):
    queryset = OptionData.objects.all()
    serializer_class = OptionDataSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['symbol', 'call_or_put']
    ordering_fields = ['strike_price', 'implied_volatility', 'expiry_date']
    ordering = ['-expiry_date']

    @swagger_auto_schema(
        operation_description="Mark this option as interesting for training or tagging purposes.",
        responses={200: openapi.Response("Flag set")}
    )
    @action(detail=True, methods=["post"])
    def mark_interesting(self, request, pk=None):
        """
        Mark the given option as interesting (future flag logic TBD).
        """
        option = self.get_object()
        return Response({"message": f"{option.symbol} marked as interesting."})

    @action(detail=False, methods=["post"])
    def fetch_now(self, request):
        symbol = request.query_params.get("symbol")
        if not symbol:
            return Response({"error": "Missing symbol"}, status=400)

        lambda_client = boto3.client("lambda", region_name="us-east-1")
        payload = {"symbol": symbol, "type": "option"}  # type 구분

        lambda_client.invoke(
            FunctionName="stock-crawler",
            InvocationType="Event",
            Payload=json.dumps(payload)
        )
        return Response({"message": f"Triggered Lambda for option data: {symbol}"})


class PriceCandleViewSet(viewsets.ModelViewSet):
    queryset = PriceCandle.objects.all()
    serializer_class = PriceCandleSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['symbol']
    ordering_fields = ['timestamp', 'close', 'volume']
    ordering = ['-timestamp']

    @swagger_auto_schema(
        operation_description="Return basic statistics for candle data.",
        responses={200: openapi.Response("Candle stats summary")}
    )
    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        Aggregate statistics over the current queryset.
        """
        qs = self.get_queryset()
        count = qs.count()
        avg_close = qs.aggregate(avg=Avg("close"))['avg']
        return Response({
            "count": count,
            "average_close": round(avg_close, 2) if avg_close else None
        })
