import re
import requests
from parsel import Selector
import json
from datetime import datetime

cookies = {
    'session-id': '257-6081315-9738356',
    'i18n-prefs': 'AED',
    'ubid-acbae': '259-5171557-0319453',
    'lc-acbae': 'en_AE',
    'session-token': '"2ckNUQhXV8Lmyg/FMUNhbeuWmMTsS+arnQRoKtFNcJoO96j9xu+9y7rw542cLEXXDwoO4pKHTXorEmMGf+xguXpAs8/9ZDPycH+wjdlxI2oRt2wRlN02qiwBwXTN8chMrevs5xvzyVrTYB+tkiy4UafFaHvYg/dhADOnN7YWsxRdOj9oyC7/AvWgcojuoZjCbil3sVuhmBv+C+8DR9qXQNWKGzYI7iP9enlREOqYbig="',
    'session-id-time': '2082787201l',
    'csm-hit': 'tb:CJP0WNZRY3BSVGB16FH3+s-4PF71H94NDEFDDJ3BME3|1668607684573&t:1668607684573&adb:adblk_yes',
}

headers = {
    'authority': 'www.amazon.ae',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,fa;q=0.7',
    'cache-control': 'max-age=0',
    # Requests sorts cookies= alphabetically
    'device-memory': '8',
    'downlink': '1.5',
    'dpr': '1.1',
    'ect': '3g',
    'rtt': '300',
    'sec-ch-device-memory': '8',
    'sec-ch-dpr': '1.1',
    'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-ch-viewport-width': '1745',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'viewport-width': '1745',
}


id = 'amazon-B09PWX3S3R'
url_id = id.split('-')[1].strip()
url = f"https://www.amazon.ae/dp/{url_id}?th=1&psc=1"
session = requests.Session()

with session.get(url,headers=headers) as response:
    response_text = response.text
    result = Selector(text=response.text)
    #############################################price##############################################################
    price_before_discount = result.css('span.a-price.a-text-price span.a-offscreen ::text').get()
    if price_before_discount:
        price_before_discount = float(price_before_discount.replace('AED', ''))
        discounted_price = float(result.css('#twister-plus-price-data-price ::attr(value)').get())
        original_price = price_before_discount
    else:
        discounted_price = 0
        original_price = float(result.css('#twister-plus-price-data-price ::attr(value)').get())

    delivery_info = result.css('span[data-csa-c-delivery-price] ::attr(data-csa-c-delivery-price)').get()
    if delivery_info:
        if not delivery_info == 'FREE':
            delivery_price = float(delivery_info.replace('AED', ''))
            original_price = original_price + delivery_price
            if not discounted_price == 0:
                discounted_price = discounted_price + delivery_price

        delivery_time = result.css('span[data-csa-c-delivery-time] ::attr(data-csa-c-delivery-time)').get()
        if '-' in delivery_time:
            delivery_split = delivery_time.split(' ')
            if len(delivery_split) == 4:
                delivery_month = delivery_time.split(' ')[0]
                delivery_month = datetime.strptime(delivery_month,'%B').month
                delivery_day = int(delivery_time.split(' ')[-1].strip())
                now = datetime.now()
                now_year = now.year
                delivery_time = datetime(year=now_year,month=delivery_month,day=delivery_day)
                difference = delivery_time - now
                day_difference = difference.days
            elif len(delivery_split) == 5:
                delivery_month = delivery_time.split(' ')[-2]
                delivery_month = datetime.strptime(delivery_month, '%B').month
                delivery_day = int(delivery_time.split(' ')[-1].strip())
                now = datetime.now()
                now_year = now.year
                delivery_time = datetime(year=now_year, month=delivery_month, day=delivery_day)
                difference = delivery_time - now
                day_difference = difference.days
        else:
            delivery_time = datetime.strptime(delivery_time, "%A, %B %d")
            now = datetime.now()
            now_year = now.year
            delivery_time = delivery_time.replace(year=now_year)
            now = datetime.now()
            difference = delivery_time - now
            day_difference = difference.days

    else:
        ########################################outside_uae###############################################################
        response_headers = dict(response.headers)
        requestId = response_headers['x-amz-rid']
        merchantId = result.css('#merchantID ::attr(value)').get()
        sessionId = result.css('#session-id ::attr(value)').get()
        csrf = re.search('csrfToken: "(\S*)",', response_text)
        csrf = csrf.groups()[0] if csrf else None
        slateToken = re.search('slateToken: "(\S*)",', response_text)
        slateToken = slateToken.groups()[0] if slateToken else None
        marketplaceId = re.search('marketplaceId: "(\S*)",', response_text)
        marketplaceId = marketplaceId.groups()[0] if marketplaceId else None
        json_data = {
            'asin': f'{id}',
            'buyingOptionIndex': '0',
            'customerId': '',
            'device': 'DESKTOP',
            'marketplaceId': f'{marketplaceId}',
            'merchantId': f'{merchantId}',
            'requestId': f'{requestId}',
            'sessionId': f'{sessionId}',
            'slateToken': f'{slateToken}',
        }

        fetch_headers = {
            'Accept': 'text/html,*/*',
            'Accept-Language': 'en_AE',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'csrf-token': f'{csrf}',
        }
        cookies = response.cookies.get_dict()
        json_data['sessionId'] = cookies['session-id']
        response_fetch = session.post('https://dcp.amazon.ae/dcp', headers=fetch_headers, json=json_data,cookies=cookies).json()
        response_content = response_fetch['content']
        response_content = Selector(response_content)
        delivery_price = response_content.css('[data-csa-c-delivery-price] ::attr(data-csa-c-delivery-price)').get()
        delivery_price = float(delivery_price.replace('AED','').strip())
        original_price = original_price + delivery_price
        if not discounted_price == 0:
            discounted_price = discounted_price + delivery_price

        delivery_time = response_content.css('span[data-csa-c-delivery-time] ::attr(data-csa-c-delivery-time)').get()
        if '-' in delivery_time:
            delivery_split = delivery_time.split(' ')
            if len(delivery_split) == 4:
                delivery_month = delivery_time.split(' ')[0]
                delivery_month = datetime.strptime(delivery_month, '%B').month
                delivery_day = int(delivery_time.split(' ')[-1].strip())
                now = datetime.now()
                now_year = now.year
                delivery_time = datetime(year=now_year, month=delivery_month, day=delivery_day)
                difference = delivery_time - now
                day_difference = difference.days
            elif len(delivery_split) == 5:
                delivery_month = delivery_time.split(' ')[-2]
                delivery_month = datetime.strptime(delivery_month, '%B').month
                delivery_day = int(delivery_time.split(' ')[-1].strip())
                now = datetime.now()
                now_year = now.year
                delivery_time = datetime(year=now_year, month=delivery_month, day=delivery_day)
                difference = delivery_time - now
                day_difference = difference.days
        else:
            delivery_time = datetime.strptime(delivery_time, "%A, %B %d")
            now = datetime.now()
            now_year = now.year
            delivery_time = delivery_time.replace(year=now_year)
            now = datetime.now()
            difference = delivery_time - now
            day_difference = difference.days

    if day_difference < 0:
        delivery_time = delivery_time.replace(year=now_year+1)
        now = datetime.now()
        difference = delivery_time - now
        day_difference = difference.days

    stock = result.css('span.a-button-inner #add-to-cart-button ::text').get()
    if stock:
        stock = 0
    else:
        stock = 5

    images = re.search('\[\{"hiRes":\S*\}\]',response_text,flags=re.DOTALL)
    if images:
        images = images.group(0)
        images = json.loads(images)
        final_images = []
        for i in images:
            hires = i['hiRes']
            large = i['large']
            if hires != None:
                final_images.append(hires)
            else:
                final_images.append(large)
    else:
        final_images = []

    product_dict = {
        'price':round(original_price,2),
        'discounted_price':round(discounted_price,2),
        'stock': stock,
        'shipping_days': day_difference,
        'images':final_images,
    }
    print(product_dict)

