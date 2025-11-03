from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from celery.result import AsyncResult
from .models import Project, Experiment, Result
from .tasks import test_myptv_task


def index_view(request):
    """
    Main view that displays all projects.
    """
    projects = Project.objects.all()
    return render(request, 'core/index.html', {
        'projects': projects
    })


def project_detail_view(request, project_id):
    """
    Detail view for a project showing its experiments.
    """
    project = get_object_or_404(Project, id=project_id)
    experiments = project.experiments.all()
    
    return render(request, 'core/project_detail.html', {
        'project': project,
        'experiments': experiments
    })


def start_experiment_view(request, project_id):
    """
    View that starts a new test experiment.
    """
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id)
        
        # 1. Create the Experiment object in the database
        experiment = Experiment.objects.create(
            project=project,
            name=request.POST.get('name', f'Experiment {project.experiments.count() + 1}'),
            status='PENDING',
            calibration_file_path='C:/ptv_platform/calibrations/test_calibration.cal',
            images_path='C:/ptv_platform/experiment_data/images/',
            used_parameters={
                'test_mode': True,
                'threshold': 100,
                'min_particle_size': 3
            },
            notes=request.POST.get('notes', '')
        )
        
        print(f"[DJANGO] Experiment created: ID={experiment.id}, Name={experiment.name}")
        
        # 2. Enqueue the Celery task
        task = test_myptv_task.delay(experiment.id)
        
        print(f"[DJANGO] Task enqueued in Celery: Task ID={task.id}")
        
        # 3. Save the Celery task ID for monitoring
        experiment.celery_task_id = task.id
        experiment.status = 'PROCESSING'
        experiment.save()
        
        print(f"[DJANGO] Task ID saved in experiment")
        
        # 4. Redirect to monitoring page
        return redirect('experiment_monitoring', experiment_id=experiment.id)
    
    # If GET, show the creation form
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'core/start_experiment.html', {
        'project': project
    })


def experiment_monitoring_view(request, experiment_id):
    """
    Monitoring view for experiment progress.
    """
    experiment = get_object_or_404(Experiment, id=experiment_id)
    
    return render(request, 'core/experiment_monitoring.html', {
        'experiment': experiment
    })


@require_http_methods(["GET"])
def get_experiment_status_view(request, experiment_id):
    """
    API endpoint that returns the current experiment status in JSON.
    Used by JavaScript to update the UI in real time.
    """
    try:
        experiment = Experiment.objects.get(id=experiment_id)
        
        data = {
            'experiment_id': experiment.id,
            'name': experiment.name,
            'status': experiment.status,
            'status_display': experiment.get_status_display(),
            'error_message': experiment.error_message,
        }
        
        # Check Celery task state if available
        if experiment.celery_task_id:
            task_result = AsyncResult(experiment.celery_task_id)
            
            data['celery_state'] = task_result.state
            data['celery_info'] = str(task_result.info) if task_result.info else None
            
            if task_result.state == 'PROGRESS':
                data['progress'] = task_result.info
        
        # Include result info if experiment is completed
        if experiment.status == 'COMPLETED':
            try:
                result = experiment.result
                data['result'] = {
                    'id': result.id,
                    'file_path': result.result_file_path,
                    'metrics': result.key_metrics
                }
            except Result.DoesNotExist:
                data['result'] = None
        
        return JsonResponse(data)
        
    except Experiment.DoesNotExist:
        return JsonResponse({
            'error': 'Experiment not found'
        }, status=404)


def result_view(request, experiment_id):
    """
    View that displays the results of a completed experiment.
    """
    experiment = get_object_or_404(Experiment, id=experiment_id)
    
    if experiment.status != 'COMPLETED':
        return redirect('experiment_monitoring', experiment_id=experiment.id)
    
    try:
        result = experiment.result
    except Result.DoesNotExist:
        result = None
    
    return render(request, 'core/result.html', {
        'experiment': experiment,
        'result': result
    })


def create_project_view(request):
    """
    View for creating a new project.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        project = Project.objects.create(
            name=name,
            description=description
        )
        
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'core/create_project.html')
