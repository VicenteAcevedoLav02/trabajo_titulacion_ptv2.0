from celery import shared_task
from django.utils import timezone
import time
from .models import Experiment, Result


@shared_task(bind=True, name='core.test_myptv_task')
def test_myptv_task(self, experiment_id):
    """
    Test task that simulates MyPTV processing.
    
    Args:
        experiment_id (int): ID of the experiment to process
        
    Returns:
        dict: Status message and result metadata
    """
    print(f"[CELERY] Starting task for Experiment ID: {experiment_id}")
    print(f"[CELERY] Celery Task ID: {self.request.id}")
    
    try:
        # 1. Retrieve experiment from database
        experiment = Experiment.objects.get(id=experiment_id)
        print(f"[CELERY] Experiment found: {experiment.name}")
        
        # 2. Update state and register start time
        experiment.state = 'PROCESSING'
        experiment.processing_start_time = timezone.now()
        experiment.save()
        print(f"[CELERY] Status updated to PROCESSING")
        
        # 3. SIMULATED MyPTV processing
        total_steps = 10
        for step in range(1, total_steps + 1):
            time.sleep(1.5)  # Simulate heavy computation
            
            # Update progress (optional)
            progress = (step / total_steps) * 100
            print(f"[CELERY] Progress: {progress:.0f}%")
            
            # Update state for Celery monitoring
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': step,
                    'total': total_steps,
                    'status': f'Processing frame {step}/{total_steps}'
                }
            )
        
        print(f"[CELERY] Simulation completed successfully")
        
        # 4. Create simulated result
        result = Result.objects.create(
            experiment=experiment,
            result_file_path=f"C:/ptv_platform/experiment_data/exp_{experiment_id}_results.csv",
            key_metrics={
                'total_particles': 10500,
                'frames_processed': 100,
                'duration_seconds': 15.0
            }
        )
        print(f"[CELERY] Result created: {result.result_file_path}")
        
        # 5. Mark experiment as COMPLETED
        experiment.state = 'COMPLETED'
        experiment.processing_end_time = timezone.now()
        experiment.save()
        print(f"[CELERY] Experiment completed successfully")
        
        return {
            'status': 'COMPLETED',
            'experiment_id': experiment_id,
            'result_id': result.id,
            'message': 'MyPTV test processing completed successfully'
        }
        
    except Experiment.DoesNotExist:
        error_msg = f"Experiment with ID {experiment_id} does not exist"
        print(f"[CELERY ERROR] {error_msg}")
        return {'status': 'ERROR', 'message': error_msg}
    
    except Exception as e:
        error_msg = f"Error during processing: {str(e)}"
        print(f"[CELERY ERROR] {error_msg}")
        
        # Update experiment with error state
        try:
            experiment = Experiment.objects.get(id=experiment_id)
            experiment.state = 'ERROR'
            experiment.error_message = error_msg
            experiment.processing_end_time = timezone.now()
            experiment.save()
        except:
            pass
        
        return {'status': 'ERROR', 'message': error_msg}
