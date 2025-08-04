from rest_framework import serializers
from .models import NewsImpact

class NewsImpactSerializer(serializers.ModelSerializer):
    sentiment = serializers.ChoiceField(
        choices=['positive', 'negative', 'neutral'],
        help_text="Sentiment classification result of the news"
    )
    score = serializers.FloatField(
        min_value=0.0,
        max_value=1.0,
        help_text="Confidence score evaluated by the LLM (0.0 ~ 1.0)"
    )
    summary = serializers.CharField(
        help_text="AI-generated summary of the news content"
    )
    related_symbols = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of related symbols mentioned in the article"
    )
    status = serializers.ChoiceField(
        choices=['analyzing', 'done', 'failed'],
        help_text="Analysis status of the news"
    )
    impact_type = serializers.ChoiceField(
        choices=[
            ('earnings', 'Earnings Report'),
            ('macro', 'Macro Event'),
            ('regulation', 'Regulatory/Legal'),
            ('product', 'Product Launch/Change'),
            ('merger', 'M&A'),
            ('technical', 'Technical Pattern'),
            ('other', 'Other')
        ],
        help_text="Categorized impact type of the news event"
    )
    ai_model_version = serializers.CharField(
        help_text="Name or version of the LLM used for the analysis (e.g., gpt-4-turbo)"
    )
    analysis_time = serializers.DateTimeField(
        read_only=True,
        help_text="Timestamp when the LLM analysis was completed"
    )
    risk_score = serializers.FloatField(
        min_value=0.0,
        max_value=1.0,
        required=False,
        allow_null=True,
        help_text="Risk evaluation score of the news impact (0.0 ~ 1.0)"
    )

    class Meta:
        model = NewsImpact
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'analysis_time']
