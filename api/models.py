from django.db import models
from django.db.models import Avg, Count
from django.utils import timezone

class Vendor(models.Model):
    name = models.CharField(max_length=100)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=50, unique=True)
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)

    def update_performance_metrics(self):
        completed_pos = self.purchaseorder_set.filter(status='completed')
        total_completed_pos = completed_pos.count()

        # Calculate on-time delivery rate
        on_time_deliveries = completed_pos.filter(delivery_date__lte=timezone.now())
        self.on_time_delivery_rate = (on_time_deliveries.count() / total_completed_pos) * 100 if total_completed_pos else 0

        # Calculate quality rating average
        self.quality_rating_avg = completed_pos.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0

        # Calculate average response time
        response_times = completed_pos.exclude(acknowledgment_date__isnull=True).annotate(
            response_time=models.ExpressionWrapper(
                models.F('acknowledgment_date') - models.F('issue_date'),
                output_field=models.DurationField()
            )
        )
        self.average_response_time = response_times.aggregate(Avg('response_time'))['response_time__avg'].total_seconds() / 60 if response_times else 0

        # Calculate fulfillment rate
        self.fulfillment_rate = (completed_pos.filter(status='completed').count() / self.purchaseorder_set.count()) * 100 if self.purchaseorder_set.count() else 0

        self.save()

    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    po_number = models.CharField(max_length=100, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    quality_rating = models.FloatField(null=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    acknowledgment_date = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'completed':
            self.vendor.update_performance_metrics()

    def __str__(self):
        return self.po_number

class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()

    def __str__(self):
        return f"{self.vendor} - {self.date}"
