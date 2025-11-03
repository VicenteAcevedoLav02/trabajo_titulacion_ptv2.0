from django.db import models
from django.utils import timezone
import json


class Project(models.Model):
    """
    Represents a research project grouping multiple experiments.
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Project's unique name"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of the project"
    )
    creation_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Automatic creation timestamp"
    )
    
    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-creation_date']
    
    def __str__(self):
        return self.name


class PresetParameters(models.Model):
    """
    Stores predefined MyPTV parameter configurations.
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Name of the preset"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this preset is for"
    )
    parameters = models.TextField(
        default="{}",
        help_text="JSON string containing all MyPTV parameters"
    )
    creation_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Automatic creation timestamp"
    )
    modification_date = models.DateTimeField(
        auto_now=True,
        help_text="Automatic last modification timestamp"
    )
    
    class Meta:
        verbose_name = "Parameter Preset"
        verbose_name_plural = "Parameter Presets"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_parameters_display(self):
        """Returns formatted parameters for display"""
        try:
            data = json.loads(self.parameters)
            return json.dumps(data, indent=2)
        except json.JSONDecodeError:
            return self.parameters


class Experiment(models.Model):
    """
    Represents an individual PTV experiment.
    """
    
    STATES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('ERROR', 'Error'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='experiments',
        help_text="Project to which this experiment belongs"
    )
    name = models.CharField(
        max_length=200,
        help_text="Descriptive name of the experiment"
    )
    creation_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Automatic creation timestamp"
    )
    processing_start_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when processing started"
    )
    processing_end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when processing ended"
    )
    
    # Experiment configuration
    calibration_file = models.CharField(
        max_length=500,
        help_text="Path to the .cal calibration file"
    )
    images_path = models.CharField(
        max_length=500,
        help_text="Path where the images are stored (RAM or SSD)"
    )
    used_parameters = models.TextField(
        default="{}",
        help_text="JSON string copy of all parameters used (for reproducibility)"
    )
    
    # Execution control
    state = models.CharField(
        max_length=20,
        choices=STATES,
        default='PENDING',
        help_text="Current state of the experiment"
    )
    celery_task_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Celery task ID for monitoring"
    )
    
    # Error information
    error_message = models.TextField(
        blank=True,
        help_text="Error message if processing failed"
    )
    
    # Researcher notes
    notes = models.TextField(
        blank=True,
        help_text="Researcher notes and observations"
    )
    
    class Meta:
        verbose_name = "Experiment"
        verbose_name_plural = "Experiments"
        ordering = ['-creation_date']
    
    def __str__(self):
        return f"{self.project.name} - {self.name} ({self.get_state_display()})"
    
    def processing_duration(self):
        """Calculates total processing duration in seconds"""
        if self.processing_start_time and self.processing_end_time:
            delta = self.processing_end_time - self.processing_start_time
            return delta.total_seconds()
        return None


class Result(models.Model):
    """
    Stores the results of a completed experiment.
    """
    experiment = models.OneToOneField(
        Experiment,
        on_delete=models.CASCADE,
        related_name='result',
        help_text="Associated experiment"
    )
    txt_file_path = models.CharField(
        max_length=500,
        help_text="Path to the .txt/.csv file containing trajectory data"
    )
    generation_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Automatic generation timestamp"
    )
    
    # Calculated metrics
    key_metrics = models.TextField(
        default="{}",
        help_text="JSON string with calculated metrics (e.g. num_particles, frames_processed)"
    )
    
    # Additional files (optional)
    additional_files = models.TextField(
        default="[]",
        help_text="JSON string list of paths to additional generated files"
    )
    
    class Meta:
        verbose_name = "Result"
        verbose_name_plural = "Results"
    
    def __str__(self):
        return f"Result of {self.experiment.name}"
    
    def get_metrics_display(self):
        """Returns formatted metrics"""
        try:
            data = json.loads(self.key_metrics)
            return json.dumps(data, indent=2)
        except json.JSONDecodeError:
            return self.key_metrics
