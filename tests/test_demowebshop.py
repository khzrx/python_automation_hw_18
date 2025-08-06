import allure
import requests
from selene import browser, have

from log_helper import response_logging, response_attaching

URL = 'https://demowebshop.tricentis.com'
EMAIL = 'ivan_ivanov@qagurutest.ru'
PASSWORD = '123123'
AUTH_COOKIE_NAME = 'NOPCOMMERCE.AUTH'


def api_request(base_api_url, endpoint, method, **kwargs):
    url = f"{base_api_url}{endpoint}"
    response = requests.request(method, url, **kwargs)
    response_logging(response)
    response_attaching(response)
    return response


def test_add_one_product_to_cart():
    with allure.step('Получить cookie авторизации через API'):
        response = api_request(
            base_api_url=URL,
            endpoint='/login',
            method='POST',
            data={'Email': EMAIL, 'Password': PASSWORD},
            allow_redirects=False
        )

        auth_cookie = response.cookies.get(AUTH_COOKIE_NAME)

    with allure.step('Добавить товар в корзину через API'):
        api_request(
            base_api_url=URL,
            endpoint='/addproducttocart/catalog/45/1/1',
            method='POST',
            cookies={AUTH_COOKIE_NAME: auth_cookie}
        )

    with allure.step('Открыть страницу корзины с переданной cookie авторизации'):
        browser.open(URL + '/cart')
        browser.driver.add_cookie({'name': AUTH_COOKIE_NAME, 'value': auth_cookie})
        browser.driver.refresh()

    with allure.step('Проверить наличие добавленного товара'):
        browser.all('.cart-item-row').should(have.size(1))
        browser.element('.product-name').should(have.text('Fiction'))
        browser.element('.product-subtotal').should(have.text('24.00'))

    with allure.step('Очистить корзину'):
        browser.element('.qty-input').set_value('0').press_enter()


def test_add_some_products_to_cart():
    with allure.step('Получить cookie авторизации через API'):
        response = api_request(
            base_api_url=URL,
            endpoint='/login',
            method='POST',
            data={'Email': EMAIL, 'Password': PASSWORD},
            allow_redirects=False
        )

        auth_cookie = response.cookies.get(AUTH_COOKIE_NAME)

    with allure.step('Добавить первый товар в корзину через API'):
        api_request(
            base_api_url=URL,
            endpoint='/addproducttocart/catalog/45/1/1',
            method='POST',
            cookies={AUTH_COOKIE_NAME: auth_cookie}
        )

    with allure.step('Добавить второй товар в корзину через API'):
        api_request(
            base_api_url=URL,
            endpoint='/addproducttocart/catalog/22/1/1',
            method='POST',
            cookies={AUTH_COOKIE_NAME: auth_cookie}
        )

    with allure.step('Открыть страницу корзины с переданной cookie авторизации'):
        browser.open(URL + '/cart')
        browser.driver.add_cookie({'name': AUTH_COOKIE_NAME, 'value': auth_cookie})
        browser.driver.refresh()

    with allure.step('Проверить наличие добавленных товаров'):
        browser.all('.cart-item-row').should(have.size(2))
        browser.all('.product-name').should(have.texts(['Fiction', 'Health Book']))
        browser.all('.product-subtotal').should(have.texts(['24.00', '10.00']))

    with allure.step('Очистить корзину'):
        quantities = browser.all('.qty-input')
        quantities[0].set_value('0')
        quantities[1].set_value('0').press_enter()