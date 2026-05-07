from django.contrib import admin

from .models import Activity, ActivityRating


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'time_takes', 'is_deleted', 'created_at', 'updated_at')
    list_filter = ('category', 'is_deleted', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return Activity.all_objects.all()


@admin.register(ActivityRating)
class ActivityRatingAdmin(admin.ModelAdmin):
    list_display = ('activity', 'user', 'rate', 'created_at')
    list_filter = ('rate', 'created_at')
    search_fields = ('activity__name', 'user__email')
    ordering = ('-created_at',)
