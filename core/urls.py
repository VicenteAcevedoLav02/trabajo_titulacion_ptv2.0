from django.urls import path
from . import views

urlpatterns = [
    # Main page
    path('', views.index_view, name='index'),

    # Project management
    path('project/create/', views.create_project_view, name='create_project_view'),
    path('project/<int:project_id>/', views.project_detail_view, name='project_detail_view'),
    
    # Experiments
    path('project/<int:project_id>/start/', views.start_experiment_view, name='start_experiment'),
    path('experiment/<int:experiment_id>/monitor/', views.experiment_monitoring_view, name='experiment_monitoring'),
    path('experiment/<int:experiment_id>/result/', views.result_view, name='experiment_result'),
    
    # API endpoints
    path('api/experiment/<int:experiment_id>/status/', views.get_experiment_status_view, name='get_experiment_status'),
]