from datetime import date as date_cls, timedelta

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from products.services.product_service import ProductService

from diary.models import Meal, MealItem
from products.models import Product

from .forms import ProfileForm, RegisterForm

MEAL_TYPES = Meal.MealType.choices
NUTRIENTS = ('calories', 'proteins', 'fats', 'carbs')


def _card_for(meal):
    return {
        'meal': meal,
        'value': meal.meal_type,
        'label': meal.get_meal_type_display(),
        'totals': meal.totals(),
        'date_iso': meal.date.isoformat(),
    }


def _day_context(profile, target):
    existing = {
        m.meal_type: m
        for m in Meal.objects.filter(profile=profile, date=target).prefetch_related('items__product')
    }
    consumed = dict.fromkeys(NUTRIENTS, 0.0)
    cards = []
    for value, label in MEAL_TYPES:
        meal = existing.get(value)
        totals = meal.totals() if meal else dict.fromkeys(NUTRIENTS, 0.0)
        for k in NUTRIENTS:
            consumed[k] += totals[k]
        cards.append({
            'meal': meal, 'value': value, 'label': label,
            'totals': totals, 'date_iso': target.isoformat(),
        })

    targets = profile.calculate_daily_targets() or {}
    remaining = {
        k: round(targets[k] - consumed[k], 1)
        for k in NUTRIENTS if targets.get(k) is not None
    }

    return {
        'cards': cards,
        'consumed': {k: round(v, 1) for k, v in consumed.items()},
        'targets': targets,
        'remaining': remaining,
        'date': target,
        'prev': target - timedelta(days=1),
        'next': target + timedelta(days=1),
    }


@login_required
def day_today(request):
    return redirect('web:day', date=timezone.localdate().isoformat())


@login_required
def day_view(request, date):
    target = date_cls.fromisoformat(date)
    return render(request, 'web/day.html', _day_context(request.user.profile, target))


@login_required
@require_POST
def create_meal(request, date, meal_type):
    target = date_cls.fromisoformat(date)
    if meal_type not in dict(MEAL_TYPES):
        raise Http404("Неизвестный тип приема пищи")
    Meal.objects.get_or_create(
        profile=request.user.profile,
        date=target,
        meal_type=meal_type,
    )
    if request.htmx:
        return render(request, 'web/partials/_day_meals.html',
                      _day_context(request.user.profile, target))
    return redirect('web:day', date=target.isoformat())


@login_required
def product_search(request):
    query = request.GET.get('q', '').strip()
    meal = None
    if request.GET.get('meal'):
        meal = get_object_or_404(Meal, pk=request.GET.get('meal'), profile__user=request.user)
    results = ProductService().search_and_import(query) if len(query) >= 2 else []
    template = ('web/partials/_products_results.html'
                if request.htmx else 'web/partials/products_search.html')
    return render(request, template, {'results': results, 'query': query, 'meal': meal})


@login_required
@require_POST
def add_product_to_meal(request, meal_id, pk):
    meal = get_object_or_404(Meal, pk=meal_id, profile__user=request.user)
    product = get_object_or_404(Product, pk=pk)
    try:
        weight = max(float(request.POST.get('weight_grams') or 100), 0.1)
    except ValueError:
        weight = 100
    MealItem.objects.create(meal=meal, product=product, weight_grams=weight)

    if request.htmx:
        return render(request, 'web/partials/_meal_card.html', {'card': _card_for(meal)})
    return redirect('web:day', date=meal.date.isoformat())


@login_required
@require_POST
def delete_item(request, pk):
    item = get_object_or_404(MealItem, pk=pk, meal__profile__user=request.user)
    meal = item.meal
    item.delete()

    if request.htmx:
        return render(request, 'web/partials/_meal_card.html', {'card': _card_for(meal)})
    return redirect('web:day', date=meal.date.isoformat())


@login_required
def profile_view(request):
    profile = request.user.profile
    form = ProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('web:profile')
    return render(request, 'web/profile.html',
                  {'form': form, 'targets': profile.calculate_daily_targets(), })

def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('web:today')
    return render(request,'registration/register.html', {'form': form})