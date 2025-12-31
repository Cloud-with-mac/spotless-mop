from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import Service, Testimonial, QuoteRequest, SiteSettings
from .forms import QuoteRequestForm
from datetime import datetime, timedelta

# Public view (homepage)
def index(request):
    """Main homepage view"""
    services = Service.objects.filter(is_active=True)
    testimonials = Testimonial.objects.filter(is_active=True)[:3]
    site_settings = SiteSettings.load()
    
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            quote_request = form.save()
            messages.success(request, "Thank you! We'll get back to you within 24 hours with your free quote.")
            return redirect('index')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = QuoteRequestForm()
    
    context = {
        'services': services,
        'testimonials': testimonials,
        'site_settings': site_settings,
        'form': form,
    }
    
    return render(request, 'cleaning/index.html', context)


# Custom Admin Views
def admin_login(request):
    """Custom admin login page"""
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password, or you do not have admin access.')
    
    return render(request, 'cleaning/admin/login.html')


@login_required(login_url='admin_login')
def admin_logout(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('admin_login')


@login_required(login_url='admin_login')
def admin_dashboard(request):
    """Main admin dashboard with statistics"""
    # Get statistics
    total_quotes = QuoteRequest.objects.count()
    new_quotes = QuoteRequest.objects.filter(status='new').count()
    total_services = Service.objects.count()
    active_services = Service.objects.filter(is_active=True).count()
    total_testimonials = Testimonial.objects.count()
    active_testimonials = Testimonial.objects.filter(is_active=True).count()
    
    # Recent quotes (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_quotes = QuoteRequest.objects.filter(created_at__gte=week_ago).count()
    
    # Latest quote requests
    latest_quotes = QuoteRequest.objects.all()[:5]
    
    # Quotes by service type
    quotes_by_service = QuoteRequest.objects.values('service').annotate(count=Count('service')).order_by('-count')
    
    context = {
        'total_quotes': total_quotes,
        'new_quotes': new_quotes,
        'total_services': total_services,
        'active_services': active_services,
        'total_testimonials': total_testimonials,
        'active_testimonials': active_testimonials,
        'recent_quotes': recent_quotes,
        'latest_quotes': latest_quotes,
        'quotes_by_service': quotes_by_service,
    }
    
    return render(request, 'cleaning/admin/dashboard.html', context)


@login_required(login_url='admin_login')
def admin_quotes_list(request):
    """List all quote requests with filters"""
    status_filter = request.GET.get('status', '')
    service_filter = request.GET.get('service', '')
    search = request.GET.get('search', '')
    
    quotes = QuoteRequest.objects.all()
    
    if status_filter:
        quotes = quotes.filter(status=status_filter)
    
    if service_filter:
        quotes = quotes.filter(service=service_filter)
    
    if search:
        quotes = quotes.filter(
            Q(name__icontains=search) | 
            Q(email__icontains=search) | 
            Q(phone__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(quotes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'service_filter': service_filter,
        'search': search,
        'status_choices': QuoteRequest.STATUS_CHOICES,
        'service_choices': QuoteRequest.SERVICE_CHOICES,
    }
    
    return render(request, 'cleaning/admin/quotes_list.html', context)


@login_required(login_url='admin_login')
def admin_quote_detail(request, pk):
    """View and update a single quote request"""
    quote = get_object_or_404(QuoteRequest, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status:
            quote.status = status
            quote.save()
            messages.success(request, f'Quote status updated to {quote.get_status_display()}')
            return redirect('admin_quote_detail', pk=pk)
    
    context = {
        'quote': quote,
        'status_choices': QuoteRequest.STATUS_CHOICES,
    }
    
    return render(request, 'cleaning/admin/quote_detail.html', context)


@login_required(login_url='admin_login')
def admin_quote_delete(request, pk):
    """Delete a quote request"""
    quote = get_object_or_404(QuoteRequest, pk=pk)
    
    if request.method == 'POST':
        quote.delete()
        messages.success(request, 'Quote request deleted successfully.')
        return redirect('admin_quotes_list')
    
    context = {'quote': quote}
    return render(request, 'cleaning/admin/quote_delete.html', context)


@login_required(login_url='admin_login')
def admin_services_list(request):
    """List all services"""
    services = Service.objects.all()
    
    context = {'services': services}
    return render(request, 'cleaning/admin/services_list.html', context)


@login_required(login_url='admin_login')
def admin_service_create(request):
    """Create a new service"""
    if request.method == 'POST':
        service = Service.objects.create(
            name=request.POST.get('name'),
            icon=request.POST.get('icon'),
            price=request.POST.get('price'),
            description=request.POST.get('description'),
            feature_1=request.POST.get('feature_1'),
            feature_2=request.POST.get('feature_2'),
            feature_3=request.POST.get('feature_3'),
            feature_4=request.POST.get('feature_4'),
            is_active=request.POST.get('is_active') == 'on',
            order=int(request.POST.get('order', 0))
        )
        messages.success(request, f'Service "{service.name}" created successfully.')
        return redirect('admin_services_list')
    
    context = {
        'icon_choices': Service.ICON_CHOICES,
    }
    return render(request, 'cleaning/admin/service_form.html', context)


@login_required(login_url='admin_login')
def admin_service_edit(request, pk):
    """Edit an existing service"""
    service = get_object_or_404(Service, pk=pk)
    
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.icon = request.POST.get('icon')
        service.price = request.POST.get('price')
        service.description = request.POST.get('description')
        service.feature_1 = request.POST.get('feature_1')
        service.feature_2 = request.POST.get('feature_2')
        service.feature_3 = request.POST.get('feature_3')
        service.feature_4 = request.POST.get('feature_4')
        service.is_active = request.POST.get('is_active') == 'on'
        service.order = int(request.POST.get('order', 0))
        service.save()
        
        messages.success(request, f'Service "{service.name}" updated successfully.')
        return redirect('admin_services_list')
    
    context = {
        'service': service,
        'icon_choices': Service.ICON_CHOICES,
        'is_edit': True,
    }
    return render(request, 'cleaning/admin/service_form.html', context)


@login_required(login_url='admin_login')
def admin_service_delete(request, pk):
    """Delete a service"""
    service = get_object_or_404(Service, pk=pk)
    
    if request.method == 'POST':
        service_name = service.name
        service.delete()
        messages.success(request, f'Service "{service_name}" deleted successfully.')
        return redirect('admin_services_list')
    
    context = {'service': service}
    return render(request, 'cleaning/admin/service_delete.html', context)


@login_required(login_url='admin_login')
def admin_testimonials_list(request):
    """List all testimonials"""
    testimonials = Testimonial.objects.all()
    
    context = {'testimonials': testimonials}
    return render(request, 'cleaning/admin/testimonials_list.html', context)


@login_required(login_url='admin_login')
def admin_testimonial_create(request):
    """Create a new testimonial"""
    if request.method == 'POST':
        testimonial = Testimonial.objects.create(
            name=request.POST.get('name'),
            location=request.POST.get('location'),
            rating=int(request.POST.get('rating', 5)),
            text=request.POST.get('text'),
            is_active=request.POST.get('is_active') == 'on',
        )
        messages.success(request, f'Testimonial from "{testimonial.name}" created successfully.')
        return redirect('admin_testimonials_list')
    
    return render(request, 'cleaning/admin/testimonial_form.html')


@login_required(login_url='admin_login')
def admin_testimonial_edit(request, pk):
    """Edit an existing testimonial"""
    testimonial = get_object_or_404(Testimonial, pk=pk)
    
    if request.method == 'POST':
        testimonial.name = request.POST.get('name')
        testimonial.location = request.POST.get('location')
        testimonial.rating = int(request.POST.get('rating', 5))
        testimonial.text = request.POST.get('text')
        testimonial.is_active = request.POST.get('is_active') == 'on'
        testimonial.save()
        
        messages.success(request, f'Testimonial from "{testimonial.name}" updated successfully.')
        return redirect('admin_testimonials_list')
    
    context = {
        'testimonial': testimonial,
        'is_edit': True,
    }
    return render(request, 'cleaning/admin/testimonial_form.html', context)


@login_required(login_url='admin_login')
def admin_testimonial_delete(request, pk):
    """Delete a testimonial"""
    testimonial = get_object_or_404(Testimonial, pk=pk)
    
    if request.method == 'POST':
        testimonial_name = testimonial.name
        testimonial.delete()
        messages.success(request, f'Testimonial from "{testimonial_name}" deleted successfully.')
        return redirect('admin_testimonials_list')
    
    context = {'testimonial': testimonial}
    return render(request, 'cleaning/admin/testimonial_delete.html', context)


@login_required(login_url='admin_login')
def admin_settings(request):
    """Manage site settings"""
    site_settings = SiteSettings.load()
    
    if request.method == 'POST':
        site_settings.phone = request.POST.get('phone')
        site_settings.email = request.POST.get('email')
        site_settings.address = request.POST.get('address')
        site_settings.hours = request.POST.get('hours')
        site_settings.facebook_url = request.POST.get('facebook_url', '')
        site_settings.twitter_url = request.POST.get('twitter_url', '')
        site_settings.instagram_url = request.POST.get('instagram_url', '')
        site_settings.linkedin_url = request.POST.get('linkedin_url', '')
        site_settings.save()
        
        messages.success(request, 'Site settings updated successfully.')
        return redirect('admin_settings')
    
    context = {'site_settings': site_settings}
    return render(request, 'cleaning/admin/settings.html', context)
