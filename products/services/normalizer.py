from typing import Optional

def _to_float(value) -> Optional[float]:
    if value in (None, '', 'unknow'):
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def normalize_off_product(raw: dict) -> Optional[dict]:
    nutriments = raw.get('nutriments', {})
    calories = _to_float(nutriments.get('energy-kcal_100g') or nutriments.get('energy-kcal'))
    proteins = _to_float(nutriments.get('proteins_100g'))
    fats = _to_float(nutriments.get('fats_100g'))
    carbs = _to_float(nutriments.get('carbs_100g'))

    # Если поле calories нет - вычисляем из БЖУ
    if calories is None and all(v is not None for v in (proteins, fats, carbs)):
        calories = round(proteins * 4 + fats * 9 + carbs * 4, 1)

    # Если у продукта нет КБЖУ - продукт бесполезен
    if all(v is None for v in (calories, proteins, fats, carbs)):
        return None

    return {
        'name': (raw.get('product_name') or '').strip() or 'Без названия',
        'brand': (raw.get('brands') or '').split(',')[0].strip(),
        'barcode': raw.get('code', ''),
        'calories': calories or 0,
        'proteins': proteins or 0,
        'fats': fats or 0,
        'carbs': carbs or 0,
    }
