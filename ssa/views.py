# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import *
from .forms import StudentEditForm, FeeCollectionForm

# User type checking decorators
def is_admin(user):
    return user.user_type == 'admin'

def is_teacher(user):
    return user.user_type == 'teacher'

def is_student(user):
    return user.user_type == 'student'

def is_admin_or_teacher(user):
    return user.user_type in ['admin', 'teacher']

# Dashboard Views
@login_required
def dashboard(request):
    if request.user.user_type == 'admin':
        return admin_dashboard(request)
    elif request.user.user_type == 'teacher':
        return teacher_dashboard(request)
    elif request.user.user_type == 'student':
        return student_dashboard(request)
    else:
        return redirect('login')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get current academic year
    current_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Calculate totals
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    
    # Fee collection statistics
    total_fees_due = FeeCollection.objects.aggregate(
        total=Sum('amount_due')
    )['total'] or 0
    
    total_fees_collected = FeeCollection.objects.aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    
    pending_fees = FeeCollection.objects.filter(
        payment_status__in=['pending', 'partial']
    ).aggregate(
        total=Sum('amount_due') - Sum('amount_paid')
    )
    pending_fees = (pending_fees['total__sum'] or 0) - (pending_fees['total__sum'] or 0)
    
    # Transport costs
    transport_revenue = FeeCollection.objects.filter(
        fee_structure__fee_type='transport',
        payment_status='paid'
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    transport_expenses = Expense.objects.filter(
        category__in=['fuel', 'transport_cost']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Food service revenue and costs
    food_revenue = FeeCollection.objects.filter(
        fee_structure__fee_type='food',
        payment_status='paid'
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    food_expenses = Expense.objects.filter(
        category='food_cost'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Total expenses
    total_expenses = Expense.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Net earnings calculation
    net_earnings = total_fees_collected - total_expenses
    
    # Recent activities
    recent_enrollments = Student.objects.order_by('-enrollment_date')[:5]
    recent_payments = FeeCollection.objects.filter(
        payment_status='paid'
    ).order_by('-payment_date')[:5]
    
    # Monthly fee collection chart data
    monthly_collections = []
    for i in range(12):
        month_start = timezone.now().replace(day=1, month=(timezone.now().month - i) % 12 + 1)
        if month_start.month == 12 and i > 0:
            month_start = month_start.replace(year=month_start.year - 1)
        
        month_end = (month_start + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        
        monthly_total = FeeCollection.objects.filter(
            payment_date__range=[month_start, month_end],
            payment_status='paid'
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        monthly_collections.append({
            'month': month_start.strftime('%b %Y'),
            'amount': float(monthly_total)
        })
    
    monthly_collections.reverse()
    
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_fees_due': total_fees_due,
        'total_fees_collected': total_fees_collected,
        'pending_fees': pending_fees,
        'transport_revenue': transport_revenue,
        'transport_expenses': transport_expenses,
        'food_revenue': food_revenue,
        'food_expenses': food_expenses,
        'total_expenses': total_expenses,
        'net_earnings': net_earnings,
        'recent_enrollments': recent_enrollments,
        'recent_payments': recent_payments,
        'monthly_collections': monthly_collections,
        'current_year': current_year,
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    
    # Get teacher's classes and subjects
    my_classes = teacher.classes.all()
    my_subjects = teacher.subjects.all()
    
    # Get students in teacher's classes
    my_students = Student.objects.filter(school_class__in=my_classes)
    
    # Recent data changes made by this teacher
    recent_changes = StudentDataChange.objects.filter(
        changed_by=teacher
    ).order_by('-timestamp')[:10]
    
    # Notifications for this teacher
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    )[:5]
    
    context = {
        'teacher': teacher,
        'my_classes': my_classes,
        'my_subjects': my_subjects,
        'my_students': my_students,
        'recent_changes': recent_changes,
        'notifications': notifications,
        'total_students': my_students.count(),
    }
    
    return render(request, 'teacher_dashboard.html', context)

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    
    # Get fee information
    fee_collections = FeeCollection.objects.filter(student=student)
    pending_fees = fee_collections.filter(payment_status__in=['pending', 'partial'])
    
    # Get notifications
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    )[:5]
    
    # Transport and food service info
    transport_assignment = TransportAssignment.objects.filter(
        student=student, is_active=True
    ).first()
    
    food_subscriptions = FoodServiceSubscription.objects.filter(
        student=student, is_active=True
    )
    
    context = {
        'student': student,
        'fee_collections': fee_collections,
        'pending_fees': pending_fees,
        'notifications': notifications,
        'transport_assignment': transport_assignment,
        'food_subscriptions': food_subscriptions,
    }
    
    return render(request, 'student_dashboard.html', context)

# Student Management Views
@login_required
@user_passes_test(is_admin_or_teacher)
def student_list(request):
    students = Student.objects.select_related('user', 'school_class').all()
    
    # Filter by class if provided
    class_filter = request.GET.get('class')
    if class_filter:
        students = students.filter(school_class__id=class_filter)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(student_id__icontains=search)
        )
    
    classes = SchoolClass.objects.all()
    
    context = {
        'students': students,
        'classes': classes,
        'selected_class': class_filter,
        'search_query': search,
    }
    
    return render(request, 'student_list.html', context)

@login_required
@user_passes_test(is_admin_or_teacher)
def student_edit(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    # Check if teacher has permission to edit this student
    if request.user.user_type == 'teacher':
        teacher = get_object_or_404(Teacher, user=request.user)
        if student.school_class not in teacher.classes.all():
            messages.error(request, "You don't have permission to edit this student.")
            return redirect('student_list')
    
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            # Track changes
            old_values = {}
            for field in form.changed_data:
                old_values[field] = getattr(student, field)
            
            form.save()
            
            # Create change records and notifications
            if request.user.user_type == 'teacher':
                teacher = Teacher.objects.get(user=request.user)
                for field in form.changed_data:
                    StudentDataChange.objects.create(
                        student=student,
                        changed_by=teacher,
                        change_type='personal_info',  # You can categorize this better
                        field_name=field,
                        old_value=str(old_values[field]),
                        new_value=str(getattr(student, field)),
                        reason=request.POST.get('reason', 'Updated by teacher')
                    )
                
                # Create notification for admin
                admin_users = CustomUser.objects.filter(user_type='admin')
                for admin in admin_users:
                    Notification.objects.create(
                        title=f"Student Data Updated: {student.user.get_full_name()}",
                        message=f"Teacher {teacher.user.get_full_name()} updated {', '.join(form.changed_data)} for student {student.user.get_full_name()}",
                        notification_type='data_change',
                        recipient=admin,
                        sender=request.user,
                        related_student=student
                    )
            
            messages.success(request, "Student information updated successfully.")
            return redirect('student_list')
    else:
        form = StudentEditForm(instance=student)
    
    context = {
        'form': form,
        'student': student,
    }
    
    return render(request, 'student_edit.html', context)

# Fee Management Views
@login_required
@user_passes_test(is_admin)
def fee_collection_list(request):
    collections = FeeCollection.objects.select_related(
        'student__user', 'fee_structure'
    ).all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        collections = collections.filter(payment_status=status_filter)
    
    # Filter by class
    class_filter = request.GET.get('class')
    if class_filter:
        collections = collections.filter(student__school_class__id=class_filter)
    
    # Summary statistics
    total_due = collections.aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    total_paid = collections.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    classes = SchoolClass.objects.all()
    
    context = {
        'collections': collections,
        'classes': classes,
        'total_due': total_due,
        'total_paid': total_paid,
        'selected_status': status_filter,
        'selected_class': class_filter,
    }
    
    return render(request, 'fee_collection_list.html', context)

@login_required
@user_passes_test(is_admin)
def collect_fee(request, collection_id):
    collection = get_object_or_404(FeeCollection, id=collection_id)
    
    if request.method == 'POST':
        form = FeeCollectionForm(request.POST, instance=collection)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.collected_by = request.user
            collection.payment_date = timezone.now()
            
            # Update payment status
            if collection.amount_paid >= collection.amount_due:
                collection.payment_status = 'paid'
            elif collection.amount_paid > 0:
                collection.payment_status = 'partial'
            
            collection.save()
            
            messages.success(request, "Fee collection recorded successfully.")
            return redirect('fee_collection_list')
    else:
        form = FeeCollectionForm(instance=collection)
    
    context = {
        'form': form,
        'collection': collection,
    }
    
    return render(request, 'collect_fee.html', context)

# Reports and Analytics
@login_required
@user_passes_test(is_admin)
def financial_reports(request):
    # Get date range from request
    start_date = request.GET.get('start_date', timezone.now().replace(day=1).date())
    end_date = request.GET.get('end_date', timezone.now().date())
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Income summary
    income_data = {
        'tuition_fees': FeeCollection.objects.filter(
            payment_date__range=[start_date, end_date],
            fee_structure__fee_type='tuition',
            payment_status='paid'
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0,
        
        'transport_fees': FeeCollection.objects.filter(
            payment_date__range=[start_date, end_date],
            fee_structure__fee_type='transport',
            payment_status='paid'
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0,
        
        'food_service_fees': FeeCollection.objects.filter(
            payment_date__range=[start_date, end_date],
            fee_structure__fee_type='food',
            payment_status='paid'
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0,
        
        'other_fees': FeeCollection.objects.filter(
            payment_date__range=[start_date, end_date],
            fee_structure__fee_type__in=['library', 'lab', 'other'],
            payment_status='paid'
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0,
    }
    
    total_income = sum(income_data.values())
    
    # Expense summary
    expense_data = {}
    for category, label in Expense.EXPENSE_CATEGORIES:
        expense_data[category] = Expense.objects.filter(
            date__range=[start_date, end_date],
            category=category
        ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_expenses = sum(expense_data.values())
    net_profit = total_income - total_expenses
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'income_data': income_data,
        'expense_data': expense_data,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
    }
    
    return render(request, 'financial_reports.html', context)

# Notifications
@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    return render(request, 'notifications_list.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        recipient=request.user
    )
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'status': 'success'})

# API Views for AJAX requests
@login_required
@user_passes_test(is_admin)
def dashboard_stats_api(request):
    stats = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'pending_fees': float(FeeCollection.objects.filter(
            payment_status__in=['pending', 'partial']
        ).aggregate(
            total=Sum('amount_due') - Sum('amount_paid')
        )['total'] or 0),
        'monthly_revenue': float(FeeCollection.objects.filter(
            payment_date__month=timezone.now().month,
            payment_status='paid'
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0)
    }
    
    return JsonResponse(stats)