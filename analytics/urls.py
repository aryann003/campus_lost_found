from django.urls import path
from .views import SummaryView, CategoryStatsView, TrendsView


urlpatterns = [
    path('summary/', SummaryView.as_view(), name='analytics-summary'),  
    path('categories/', CategoryStatsView.as_view(), name='analytics-categories'),
    path('trends/', TrendsView.as_view(), name='analytics-trends'), 
]