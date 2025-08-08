# urls.py (app-level)
from django.urls import path
# from . import views

app_name = 'ssa'

urlpatterns = [
    # Authentication URLs
    # path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Student Management URLs
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_add, name='student_add'),
    path('students/<int:student_id>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:student_id>/view/', views.student_view, name='student_view'),
    path('students/<int:student_id>/delete/', views.student_delete, name='student_delete'),
    
    # Teacher Management URLs
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/add/', views.teacher_add, name='teacher_add'),
    path('teachers/<int:teacher_id>/edit/', views.teacher_edit, name='teacher_edit'),
    path('teachers/<int:teacher_id>/view/', views.teacher_view, name='teacher_view'),
    path('teachers/<int:teacher_id>/delete/', views.teacher_delete, name='teacher_delete'),
    
    # Fee Management URLs
    path('fees/', views.fee_collection_list, name='fee_collection_list'),
    path('fees/structure/', views.fee_structure_list, name='fee_structure_list'),
    path('fees/structure/add/', views.fee_structure_add, name='fee_structure_add'),
    path('fees/structure/<int:structure_id>/edit/', views.fee_structure_edit, name='fee_structure_edit'),
    path('fees/collect/<int:collection_id>/', views.collect_fee, name='collect_fee'),
    path('fees/generate/', views.generate_fees, name='generate_fees'),
    path('fees/bulk-collection/', views.bulk_fee_collection, name='bulk_fee_collection'),
    
    # Transport Management URLs
    path('transport/routes/', views.transport_route_list, name='transport_route_list'),
    path('transport/routes/add/', views.transport_route_add, name='transport_route_add'),
    path('transport/routes/<int:route_id>/edit/', views.transport_route_edit, name='transport_route_edit'),
    path('transport/assignments/', views.transport_assignment_list, name='transport_assignment_list'),
    path('transport/assign/<int:student_id>/', views.assign_transport, name='assign_transport'),
    
    # Food Service Management URLs
    path('food-service/', views.food_service_list, name='food_service_list'),
    path('food-service/add/', views.food_service_add, name='food_service_add'),
    path('food-service/<int:service_id>/edit/', views.food_service_edit, name='food_service_edit'),
    path('food-service/subscriptions/', views.food_subscription_list, name='food_subscription_list'),
    path('food-service/subscribe/<int:student_id>/', views.subscribe_food_service, name='subscribe_food_service'),
    
    # Expense Management URLs
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    path('expenses/<int:expense_id>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:expense_id>/delete/', views.expense_delete, name='expense_delete'),
    
    # Class and Subject Management URLs
    path('classes/', views.school_class_list, name='school_class_list'),
    path('classes/add/', views.school_class_add, name='school_class_add'),
    path('classes/<int:class_id>/edit/', views.school_class_edit, name='school_class_edit'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.subject_add, name='subject_add'),
    path('subjects/<int:subject_id>/edit/', views.subject_edit, name='subject_edit'),
    
    # Reports URLs
    path('reports/financial/', views.financial_reports, name='financial_reports'),
    path('reports/student/', views.student_reports, name='student_reports'),
    path('reports/fee-collection/', views.fee_collection_reports, name='fee_collection_reports'),
    path('reports/transport/', views.transport_reports, name='transport_reports'),
    path('reports/food-service/', views.food_service_reports, name='food_service_reports'),
    
    # Notification URLs
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/send/', views.send_notification, name='send_notification'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/bulk-send/', views.bulk_send_notification, name='bulk_send_notification'),
    
    # Academic Year URLs
    path('academic-years/', views.academic_year_list, name='academic_year_list'),
    path('academic-years/add/', views.academic_year_add, name='academic_year_add'),
    path('academic-years/<int:year_id>/edit/', views.academic_year_edit, name='academic_year_edit'),
    path('academic-years/<int:year_id>/set-current/', views.set_current_year, name='set_current_year'),
    
    # API URLs
    path('api/dashboard-stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('api/monthly-revenue/', views.monthly_revenue_api, name='monthly_revenue_api'),
    path('api/fee-collection-chart/', views.fee_collection_chart_api, name='fee_collection_chart_api'),
    path('api/student-class-distribution/', views.student_class_distribution_api, name='student_class_distribution_api'),
    path('api/expense-category-chart/', views.expense_category_chart_api, name='expense_category_chart_api'),
    
    # Export URLs
    path('export/students/', views.export_students, name='export_students'),
    path('export/teachers/', views.export_teachers, name='export_teachers'),
    path('export/fee-collections/', views.export_fee_collections, name='export_fee_collections'),
    path('export/expenses/', views.export_expenses, name='export_expenses'),
    path('export/financial-report/', views.export_financial_report, name='export_financial_report'),
    
    # Bulk Operations URLs
    path('bulk/import-students/', views.bulk_import_students, name='bulk_import_students'),
    path('bulk/generate-fee-collections/', views.bulk_generate_fee_collections, name='bulk_generate_fee_collections'),
    path('bulk/send-fee-reminders/', views.bulk_send_fee_reminders, name='bulk_send_fee_reminders'),
    
    # Settings URLs
    path('settings/', views.settings_view, name='settings'),
    path('settings/backup/', views.backup_data, name='backup_data'),
    path('settings/restore/', views.restore_data, name='restore_data'),
]
