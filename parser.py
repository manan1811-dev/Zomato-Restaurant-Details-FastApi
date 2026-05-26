from request import * 
from lxml import html 
import re 
import json 
from urllib.parse import urljoin
def get_page_json(url):
    data = request(url)
    tree = html.fromstring(data)
    script = tree.xpath("//script/text()")
    for s in script:
        if 'window.__PRELOADED_STATE__' in s[:1000]:
            match = re.search(r'JSON\.parse\("(.*)"\)', s)
            json_str = match.group(1)
            json_str = json_str.encode().decode('unicode_escape')
            break

    resturant_response = json.loads(json_str)

    return resturant_response     


def parser(url):
    orders_result = None
    #overview request

    page_json = get_page_json(url)
    main_url = 'https://www.zomato.com/'
    images = []
    if page_json.get('pages'):
        outlet = page_json.get('pages').get('current').get('pageTitle')
        res_id = page_json.get('pages').get('current').get('resId')
        page_url = page_json.get('pages').get('current').get('canonicalUrl')

        res_data_path = page_json.get('pages').get('restaurant').get(str(res_id)).get('sections')

        basic_info_path = res_data_path.get('SECTION_BASIC_INFO')

        rating = float(basic_info_path.get('rating').get('aggregate_rating',0)) or 0
        votes = int(basic_info_path.get('rating').get('votes',0)) or 0
        dining_rating = basic_info_path.get('rating_new').get('ratings').get('DINING').get('rating',0) or 0
        review_count = basic_info_path.get('rating_new').get('ratings').get('DINING').get('reviewCount',0) or 0
        open_status = basic_info_path.get('res_status_text') or None
        timing = basic_info_path.get('timing').get('customised_timings').get('opening_hours') or None


    # order api 

    order_url = f"https://www.zomato.com/webroutes/getPage?page_url={url.split('https://www.zomato.com/')[1]}/order&location=&isMobile=0"    
    order_api_response = request(order_url)
    order_api_response = json.loads(order_api_response)
    if order_api_response.get('page_data'):

        header_detaile = res_data_path.get('SECTION_RES_HEADER_DETAILS')
        cusine = [i.get('name') for i in header_detaile.get('CUISINES')] or None

        contanct_details = res_data_path.get('SECTION_RES_CONTACT')
        pincode = contanct_details.get('zipcode') or None
        lat = contanct_details.get('latitude') or None
        lng = contanct_details.get('longitude') or None
        map_url = contanct_details.get('static_map_url') or None
        address = contanct_details.get('address') or None
        phone_no =contanct_details.get('phoneDetails').get('phoneStr') or None


        menu_main_path = (
            (order_api_response.get('page_data') or {})
            .get('order') or {}
        )

        menu_main_path = (menu_main_path.get('menuList') or {}).get('menus') or []
        menu_list = []

        for menu_data in menu_main_path:
            menu_name = menu_data["menu"]["name"]
            menu_dict = {
                "menu_name": menu_name,
                "items": []
            }
            categories = menu_data["menu"].get("categories", [])
            for category_data in categories:
                items = category_data["category"].get("items", [])
                for item_data in items:
                    item = item_data["item"]
                    menu_dict["items"].append({
                        "name": item.get("name"),
                        "description": item.get("desc"),
                        "imageurl": item.get("item_image_url")
                    })
            menu_list.append(menu_dict)

            orders_result = {
                'address':address,
                'pincode':pincode,
                'phone_no':phone_no,
                'map_url':map_url,
                'lng':lng,
                'lat':lat,
                'cusine':cusine,
                'dining_rating':dining_rating,
                "menu_list":menu_list
            }

    #photo api
    photo_url = f"https://www.zomato.com/webroutes/getPage?page_url={url.split('https://www.zomato.com/')[1]}/photos&location=&isMobile=0"    
    photos_request = request(photo_url)
    photos_request = json.loads(photos_request)

    if photos_request.get('page_data').get('sections'):
        photo_path =photos_request.get('page_data').get('sections')
        image_ids = photo_path.get('SECTION_GALLERY_PHOTOS').get('entities')
        main_img_path = photos_request.get('entities').get('IMAGES')
        for i in image_ids:
            if i.get('entity_type') == 'IMAGES':
                ids = i.get('entity_ids')
                for id in ids:
                    images.append(main_img_path.get(id).get('url'))

    #menu api 
    menu_items = []
    menu_url = f"https://www.zomato.com/webroutes/getPage?page_url={url.split('https://www.zomato.com/')[1]}/menu&location=&isMobile=0"    
    menu_api_response = request(menu_url)
    menu_api_response = json.loads(menu_api_response)
    if menu_api_response.get('page_data').get('sections'):
        menu_path =menu_api_response.get('page_data').get('sections').get('SECTION_IMAGE_MENU').get('menuItems')
        for m in menu_path:
            menu_items.append({
                'label':m.get('label'),
                'pages_images':[i.get('url') for i in m.get('pages')]
            })

    return {
        'outlet':outlet,
        'res_id':res_id,
        'page_url':page_url,
        'rating':rating,
        'votes':votes,
        'review_count':review_count,
        'open':open_status,
        'timing':timing,
        'images':images or None,
        'order':orders_result or None,
        'menu_items':menu_items or None
    }  
