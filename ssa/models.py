# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from decimal import Decimal

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SchoolClass(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Grade 1", "Form 4"
    section = models.CharField(max_length=10, blank=True)  # e.g., "A", "B"
    capacity = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.section}" if self.section else self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    subjects = models.ManyToManyField(Subject)
    classes = models.ManyToManyField(SchoolClass)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    hire_date = models.DateField()
    qualification = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)
    enrollment_date = models.DateField(default=timezone.now)
    is_transport_user = models.BooleanField(default=False)
    is_food_service_user = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.student_id}"

class FeeStructure(models.Model):
    FEE_TYPES = (
        ('tuition', 'Tuition Fee'),
        ('transport', 'Transport Fee'),
        ('food', 'Food Service Fee'),
        ('library', 'Library Fee'),
        ('lab', 'Laboratory Fee'),
        ('other', 'Other Fee'),
    )
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_mandatory = models.BooleanField(default=True)
    academic_year = models.CharField(max_length=9)  # e.g., "2024-2025"
    
    class Meta:
        unique_together = ['school_class', 'fee_type', 'academic_year']

class FeeCollection(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
    )
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('cheque', 'Cheque'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField()
    receipt_number = models.CharField(max_length=50, blank=True)
    collected_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TransportRoute(models.Model):
    route_name = models.CharField(max_length=100)
    pickup_points = models.TextField()  # JSON field to store multiple pickup points
    monthly_fee = models.DecimalField(max_digits=8, decimal_places=2)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15)
    vehicle_number = models.CharField(max_length=20)
    capacity = models.IntegerField()
    
    def __str__(self):
        return self.route_name

class TransportAssignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    route = models.ForeignKey(TransportRoute, on_delete=models.CASCADE)
    pickup_point = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class FoodService(models.Model):
    MEAL_TYPES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    )
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPES)
    daily_rate = models.DecimalField(max_digits=6, decimal_places=2)
    monthly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

class FoodServiceSubscription(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    food_service = models.ForeignKey(FoodService, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

class Expense(models.Model):
    EXPENSE_CATEGORIES = (
        ('fuel', 'Fuel'),
        ('maintenance', 'Maintenance'),
        ('supplies', 'Supplies'),
        ('utilities', 'Utilities'),
        ('salary', 'Salary'),
        ('food_cost', 'Food Service Cost'),
        ('transport_cost', 'Transport Cost'),
        ('other', 'Other'),
    )
    
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    receipt_number = models.CharField(max_length=50, blank=True)
    vendor = models.CharField(max_length=100, blank=True)
    recorded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.category} - {self.amount} on {self.date}"

class StudentDataChange(models.Model):
    CHANGE_TYPES = (
        ('personal_info', 'Personal Information'),
        ('academic_info', 'Academic Information'),
        ('contact_info', 'Contact Information'),
        ('fee_info', 'Fee Information'),
        ('transport_info', 'Transport Information'),
        ('food_service_info', 'Food Service Information'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    changed_by = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES)
    field_name = models.CharField(max_length=100)
    old_value = models.TextField()
    new_value = models.TextField()
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student} - {self.field_name} changed by {self.changed_by}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('data_change', 'Data Change'),
        ('fee_reminder', 'Fee Reminder'),
        ('general', 'General'),
        ('transport', 'Transport'),
        ('food_service', 'Food Service'),
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=15, choices=NOTIFICATION_TYPES)
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications')
    is_read = models.BooleanField(default=False)
    related_student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class AcademicYear(models.Model):
    year = models.CharField(max_length=9, unique=True)  # e.g., "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    def __str__(self):
        return self.year
    
    def save(self, *args, **kwargs):
        if self.is_current:
            # Ensure only one academic year is current
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)
