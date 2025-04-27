from django.db import models
from core.models import BaseModel
from core.choices import AnalysisStatus
from crawling_system.models import NewsArticle

class NewsImpact(BaseModel):
    news = models.OneToOneField(
        NewsArticle,
        on_delete=models.CASCADE,
        related_name='impact'
    )
    sentiment = models.CharField(
        max_length=10,
        choices=[('positive', 'Positive'), ('negative', 'Negative'), ('neutral', 'Neutral')]
    )
    score = models.FloatField(help_text="Confidence score (0.0 ~ 1.0)")
    summary = models.TextField()
    related_symbols = models.JSONField(default=list)
    status = models.CharField(
        max_length=20,
        choices=AnalysisStatus.choices,
        default=AnalysisStatus.ANALYZING
    )

    def __str__(self):
        return f"[{self.news.symbol}] {self.sentiment} ({self.score})"


    web version --


    app - >   standdard - > sdfs preimsid -> 실시간

    slack

    피터는

    1. anaylzer - transcription -> 주식에 얼마나 영향도  (news / )
    2. option anaylzer
    3. chart - candle - 파동  - 패턴 -> anaylzer ( rollver over window ) 5분봉 15분 30분봉 1시간봉 1주
        볼린전  (볼린저벤터 하단 값이 - 몇퍼센트 cancdle 초과 + candle length  )

    상승장이

    지지를 서포트


너가 시드가 얼마던 현금얼
max call wall -> 캔들모양 -> 다이버전스

스윙 단기 자익로


ㅅ윙 다닉

이시점에 리스크가 트리거가

주식 찐으로 내려가느지도  개미꼬시기

1.
vix - 갑자기 이상하다 50 불짜리가  4월중순

hedge
4월달에 4700 4800

4얼
4800


1. 사람마다 공격적으로 (하루종일 )
2. 지지선 확인 확인학은한
3. 추세를 보고하는사람들
4. 장기투자라서 1차 사놓고


룸메 친구들이 인풀루언서들 ()


2. scope


480 매수 유리 하수이

470 이개 ㅅ 헷지를

매수 구간 이거나

사촌동생











