# Las Reglas de Cancelación siguen la siguiente estructura:
# ['Más de X días', 'Menos de Y días', 'Z % de devolución de la pre-reserva']

reglas_cancelacion = [
    [7, None, 100], # Las cancelaciones realizadas con más de 7 días (8 en adelante) de antelación reciben el 100% de la pre-reserva de vuelta
    [3, 8, 75], # Las cancelaciones realizadas con entre 4 y 7 días de antelación (Más que 3 y Menos que 8), reciben el 75% de la pre-reserva de vuelta
    [0, 4, 50], # Las cancelaciones realizadas con entre 1 y 3 días de antelación (Más que 0 y Menos que 4), reciben el 50% de la pre-reserva de vuelta
    [-1, 1, 0], # Las cancelaciones realizadas el mismo día de la Reserva (0 días de antelación) (Más que -1 y Menos que 1), no reciben ninguna devolución de la pre-reserva
]