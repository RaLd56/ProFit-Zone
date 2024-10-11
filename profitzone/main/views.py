from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .forms import LoginForm, RegisterForm
from .models import SwedishWall, HorizontalBar, Nutrition, WeightliftingProduct, Product, Cart, CartItem, FitnessProduct, BarbellRack, MartialArtsProduct
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import uuid
from yookassa import Configuration, Payment
Configuration.account_id = 462847
Configuration.secret_key = 'test_sneaHyRCKhgMHiDIqMPugDW_q3rV4KQ5UBzfSWCDI1M'
from dadata import Dadata
import re

dadata_token = '379f5d20568c976d8fe913e09fcf6491bd12a01c'
dadata_secret = '37667482de471ccda2255440bb3de579ad51ffdf'

def delivery(request):
    return render(request, 'main/free_delivery.html')


def login_view(request):
    if request.method == 'POST':
        login_form = LoginForm(request, data=request.POST)

        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            return JsonResponse({'success': True})  

        return JsonResponse({'success': False, 'error': 'Неверные учетные данные'}, status=400)

def register_view(request):
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)

        if register_form.is_valid():
            register_form.save()  
            user = authenticate(username=register_form.cleaned_data['username'],
                                password=register_form.cleaned_data['password1'])
            if user:
                login(request, user)  
                return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Ошибка регистрации. Проверьте введенные данные.'}, status=400)

def homepage(request):
    login_form = LoginForm()
    register_form = RegisterForm()
    return render(request, 'main/homepage.html', {
        'login_form': login_form,
        'register_form': register_form,
    })

def catalogue(request):
    login_form = LoginForm()
    register_form = RegisterForm()

    sort_by = request.GET.get('sort_by', 'popularity')
    min_price = request.GET.get('min_price', 1690)
    max_price = request.GET.get('max_price', 38990)
    category = request.GET.get('category')
    


    products = Product.objects.all()    


    if category:
        if category == 'Шведские стенки':
            products = SwedishWall.objects.all()
        elif category == 'Турники':
            products = HorizontalBar.objects.all()
        elif category == 'Спортивное питание':
            products = Nutrition.objects.all()
        elif category == 'Тяжелая атлетика':
            products = WeightliftingProduct.objects.all()
        elif category == 'Фитнес':
            products = FitnessProduct.objects.all()
        elif category == 'Стойки для штанг':
            products = BarbellRack.objects.all()
        elif category == 'Единоборства':
            products = MartialArtsProduct.objects.all()
        else:
            products = Product.objects.all()  
    else:
        products = Product.objects.all()  

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    print(category)
    if sort_by == 'price':
        products = products.order_by('price')
    else:
        products = products.order_by('-popularity')
    print(products)

    context = {
        'products_sort': products,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'category': category,
        'login_form': login_form,
        'register_form': register_form,
    }

    # Если это AJAX-запрос, возвращаем только часть с товарами
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/includes/catalogue_list.html', context)

    return render(request, 'main/catalogue.html', context)


def product_card(request, id):
    login_form = LoginForm()
    register_form = RegisterForm()
    product = Product.objects.get(id=id)
    product.popularity += 1
    product.save()
    product = get_object_or_404(Product, id=id)
    return render(request, 'main/product_card.html', {'product': product, 'login_form': login_form, 'register_form': register_form})

@require_POST
def update_quantity(request):
    try:
        cart = Cart.objects.get(user=request.user)
        item_id = request.POST.get('item_id')
        new_quantity = int(request.POST.get('quantity'))
        
        cart_item = CartItem.objects.get(id=item_id, cart=cart)

        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
            response = {'status': 'success', 'total_price': cart_item.get_total_price(), 'cart_total': cart.get_total_price()}
        else:
            response = {'status': 'error', 'message': 'Количество должно быть больше 0'}
        
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
def remove_item(request):
    try:
        cart = Cart.objects.get(user=request.user)
        item_id = request.POST.get('item_id')
        
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        cart_item.delete()
        
        response = {'status': 'success', 'cart_total': cart.get_total_price()}
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
@login_required
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product does not exist'}, status=404)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    return JsonResponse({'status': 'success', 'message': 'Product added to cart', 'cart_quantity': cart_item.quantity})

def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'main/cart.html', {'cart':cart})
def swedish_walls(request):
    login_form = LoginForm()
    register_form = RegisterForm()
    COLOR_MAP = {
        'Белый': 'white',
        'Черный': 'black',
        'Желтый': 'yellow',
        'Все цвета': 'all'
    }
    sort_by = request.GET.get('sort_by', 'popularity')
    min_price = request.GET.get('min_price', 8990)
    max_price = request.GET.get('max_price', 24990)
    color = request.GET.get('color')
    load_limits = request.GET.get('load_limits')


    

    selected_color_eng = COLOR_MAP.get(color)
    # Фильтруем товары по цене и выбранным фильтрам
    walls = SwedishWall.objects.filter(price__gte=min_price, price__lte=max_price)

    if selected_color_eng == 'all' or selected_color_eng == None:
        pass
    else:
        walls = walls.filter(color=selected_color_eng)
    


    if load_limits == 'Любой' or load_limits == None:
        pass
    else:
        walls = walls.filter(max_load=load_limits)

    
    # Сортируем товары
    if sort_by == 'price':
        walls = walls.order_by('price')
    else:
        walls = walls.order_by('-popularity')

    print(walls)
    context = {
        'swedish_walls_sort': walls,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'colors': color,
        'load_limits': load_limits,
        'login_form': login_form,
        'register_form': register_form,
    }

    # Если это AJAX-запрос, возвращаем только часть с товарами
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/includes/swedish_walls_list.html', context)

    return render(request, 'main/swedish_walls.html', context)

def horizontal_bars(request):
    login_form = LoginForm()
    register_form = RegisterForm()
    COLOR_MAP = {
        'Серебряный': 'silver',
        'Белый': 'white',
        'Черный': 'black',
        'Желтый': 'yellow',
        'Синий': 'blue',
        'Все цвета': 'all'
    }
    sort_by = request.GET.get('sort_by', 'popularity')
    min_price = request.GET.get('min_price', 2990)
    max_price = request.GET.get('max_price', 15990)
    color = request.GET.get('color')
    load_limits = request.GET.get('load_limits')
    


    

    selected_color_eng = COLOR_MAP.get(color)
    # Фильтруем товары по цене и выбранным фильтрам
    bars = HorizontalBar.objects.filter(price__gte=min_price, price__lte=max_price)



    if selected_color_eng == 'all' or selected_color_eng == None:
        pass
    else:
        bars = bars.filter(color=selected_color_eng)


    if load_limits == 'Любой' or load_limits == None:
        pass
    else:
        bars = bars.filter(max_load=load_limits)

    # Сортируем товары
    if sort_by == 'price':
        bars = bars.order_by('price')
    else:
        bars = bars.order_by('-popularity')

    context = {
        'horizontal_bars_sort': bars,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'colors': color,
        'load_limits': load_limits,
        'login_form': login_form,
        'register_form': register_form,
    }

    # Если это AJAX-запрос, возвращаем только часть с товарами
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/includes/horizontal_bars_list.html', context)

    return render(request, 'main/horizontal_bars.html', context)

def nutrition(request):
    login_form = LoginForm()
    register_form = RegisterForm()

    sort_by = request.GET.get('sort_by', 'popularity')
    min_price = request.GET.get('min_price', 1690)
    max_price = request.GET.get('max_price', 3990)
    category = request.GET.get('category')
    flavour = request.GET.get('flavour')



    nutrition = Nutrition.objects.filter(price__gte=min_price, price__lte=max_price)



    if category == 'Любая категория' or category == None:
        pass
    else:
        nutrition = nutrition.filter(category=category)
        

    if flavour == 'Любой' or flavour == None:
        pass
    else:
        print(flavour)
        nutrition = nutrition.filter(flavor=flavour)

    # Сортируем товары
    if sort_by == 'price':
        nutrition = nutrition.order_by('price')
    else:
        nutrition = nutrition.order_by('-popularity')

    context = {
        'nutrition_sort': nutrition,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'category': category,
        'flavour': flavour,
        'login_form': login_form,
        'register_form': register_form,
    }

    # Если это AJAX-запрос, возвращаем только часть с товарами
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/includes/nutrition_list.html', context)

    return render(request, 'main/nutrition.html', context)

def lifting(request):
    login_form = LoginForm()
    register_form = RegisterForm()

    sort_by = request.GET.get('sort_by', 'popularity')
    min_price = request.GET.get('min_price', 2990)
    max_price = request.GET.get('max_price', 38990)
    weight = request.GET.get('weight')
    category = request.GET.get('category')
    print(category)



    lifting = WeightliftingProduct.objects.filter(price__gte=min_price, price__lte=max_price)
    


    if category == 'Любая категория' or category == None:
        pass
    else:
        lifting = lifting.filter(category=category)
        

    if weight == 'Любой' or weight == None:
        pass
    else:
        lifting = lifting.filter(weight=weight)

    # Сортируем товары
    if sort_by == 'price':
        lifting = lifting.order_by('price')
    else:
        lifting = lifting.order_by('-popularity')

    context = {
        'lifting_sort': lifting,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'category': category,
        'weight': weight,
        'login_form': login_form,
        'register_form': register_form,
    }

    # Если это AJAX-запрос, возвращаем только часть с товарами
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/includes/lifting_list.html', context)

    return render(request, 'main/lifting.html', context)

def racks(request):
    login_form = LoginForm()
    register_form = RegisterForm()
    ADJUSTABLE_MAP = {
        'Да': True,
        'Нет': False,
    }
    


    sort_by = request.GET.get('sort_by', 'popularity')
    min_price = request.GET.get('min_price', 7990)
    max_price = request.GET.get('max_price', 25990)
    weight = request.GET.get('weight')
    adjustable = request.GET.get('adjustable')

    selected_adjustability = ADJUSTABLE_MAP.get(adjustable)

    racks = BarbellRack.objects.filter(price__gte=min_price, price__lte=max_price)
    


    if adjustable == 'Неважно' or adjustable == None:
        pass
    else:
        racks = racks.filter(adjustable=selected_adjustability)
        

    if weight == 'Любой' or weight == None:
        pass
    else:
        racks = racks.filter(max_load=weight)

    # Сортируем товары
    if sort_by == 'price':
        racks = racks.order_by('price')
    else:
        racks = racks.order_by('-popularity')

    context = {
        'racks_sort': racks,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'adjustable': adjustable,
        'weight': weight,
        'login_form': login_form,
        'register_form': register_form,
    }

    # Если это AJAX-запрос, возвращаем только часть с товарами
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/includes/racks_list.html', context)

    return render(request, 'main/racks.html', context)

def fitness(request):
    login_form = LoginForm()
    register_form = RegisterForm()

    


    sort_by = request.GET.get('sort_by', 'popularity')
    min_price = request.GET.get('min_price', 500)
    max_price = request.GET.get('max_price', 3990)
    category = request.GET.get('category')


    product = FitnessProduct.objects.filter(price__gte=min_price, price__lte=max_price)
    


    if category == 'Любая категория' or category == None:
        pass
    else:
        product = product.filter(category=category)
        

    # Сортируем товары
    if sort_by == 'price':
        product = product.order_by('price')
    else:
        product = product.order_by('-popularity')

    context = {
        'fitness_sort': product,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'login_form': login_form,
        'register_form': register_form,
        'category': category
    }

    # Если это AJAX-запрос, возвращаем только часть с товарами
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/includes/fitness_list.html', context)

    return render(request, 'main/fitness.html', context)

def martial_arts(request):
    login_form = LoginForm()
    register_form = RegisterForm()

    # Словарь для сопоставления русских названий категорий с внутренними значениями модели
    CATEGORY_CHOICES = {
        'Перчатки': 'gloves',
        'Шлем': 'helmet',
        'Форма': 'uniform',
        'Груша': 'bag',
        'Защита': 'protector',
        'Любая категория': None
    }

    # Получение параметров запроса
    sort_by = request.GET.get('sort_by', 'popularity')
    min_price = request.GET.get('min_price', 4890)
    max_price = request.GET.get('max_price', 11000)
    category = request.GET.get('category', 'Любая категория')

    # Преобразуем русское значение категории в внутреннее значение модели
    category_value = CATEGORY_CHOICES.get(category)

    # Фильтрация по цене
    products = MartialArtsProduct.objects.filter(price__gte=min_price, price__lte=max_price)
    
    if category_value == 'Любая категория' or category_value == None:
        print('huy')
        pass
    else:
        print(category)
        products = products.filter(category=category_value)


    # Сортируем товары
    if sort_by == 'price':
        products = products.order_by('price')
    else:
        products = products.order_by('-popularity')

    context = {
        'products_sort': products,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'login_form': login_form,
        'register_form': register_form,
        'category': category,  # Добавляем категорию для отображения в шаблоне
    }
    print(category)

    # Если это AJAX-запрос, возвращаем только часть с товарами
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main/includes/martial_arts_list.html', context)

    # Возвращаем полный рендер
    return render(request, 'main/martial_arts.html', context)


@login_required
def order(request):
    cart = Cart.objects.get(user=request.user)
    delivery_price = 500
    
    if request.method == 'POST':
        # Проверяем, выбран ли самовывоз
        if 'pickup' in request.POST:
            # Если самовывоз, сразу переходим к оплате
            value = cart.get_total_price() + delivery_price
            if value >= 3000:
                value = cart.get_total_price()
            payment = Payment.create({
                "amount": {
                    "value": value,
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "http://127.0.0.1:8000/cart"
                },
                "capture": True,
                "description": "Заказ №1"
            }, uuid.uuid4())
            confirmation_url = payment.confirmation.confirmation_url
            return redirect(confirmation_url)
        
        # Если самовывоз не выбран, продолжаем с обработкой адреса
        token = dadata_token
        secret = dadata_secret
        dadata = Dadata(token, secret)
        address = request.POST.get('address')
        print(address)
        try:
            result = dadata.clean("address", address)
            if result.get('qc') == 0: 
                found_address = result.get('result')
                print(found_address)
                value = cart.get_total_price() + delivery_price
                if value >= 3000:
                    value = cart.get_total_price()
                payment = Payment.create({
                    "amount": {
                        "value": value,
                        "currency": "RUB"
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": "http://127.0.0.1:8000/cart"
                    },
                    "capture": True,
                    "description": "Заказ №1"
                }, uuid.uuid4())
                confirmation_url = payment.confirmation.confirmation_url
                return redirect(confirmation_url)

            else:  # Адрес не найден
                error_message = "Такого адреса нет"
                print(error_message)
                return render(request, 'main/order.html', {
                    'error_message': error_message, 'delivery_price': delivery_price
                })
        except Exception as e:
            print(f"Ошибка при обращении к Dadata API: {e}")
            error_message = "Ошибка при обработке адреса"
            return render(request, 'main/order.html', {
                'error_message': error_message, 'delivery_price': delivery_price
            })
    return render(request, 'main/order.html', {'cart': cart, 'delivery_price': delivery_price})

def about(request):
    return render(request, 'main/about.html')

def contacts(request):
    return render(request, 'main/contacts.html')