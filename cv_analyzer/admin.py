from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import JobPosition, Applicant, CVAnalysis

@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_by',)

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'job_position', 'uploaded_at')
    list_filter = ('job_position',)
    search_fields = ('full_name', 'email')
    readonly_fields = ('uploaded_at',)

@admin.register(CVAnalysis)
class CVAnalysisAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'get_overall_score', 'analyzed_at')
    search_fields = ('applicant__full_name',)
    readonly_fields = ('analyzed_at',)

    @admin.display(description='Overall Score')
    def get_overall_score(self, obj):
        # Safely get the score from the JSONField
        if isinstance(obj.scorecard, dict):
            return obj.scorecard.get('final_assessment', {}).get('overall_score', 'N/A')
        return 'N/A'
