from lxml import html
from request import request
import re
import json
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
    return json_str

def parser(url,get_id):
    json_str = get_page_json(url)
    data= json.loads(json_str)
    res_id=data.get("pages").get("current").get("resId")
    res_name=data.get("pages").get("restaurant").get(str(res_id)).get("sections").get("SECTION_BASIC_INFO").get("name")
    res_cuisine=data.get("pages").get("restaurant").get(str(res_id)).get("sections").get("SECTION_BASIC_INFO").get("cuisine_string")
    rating_data=data.get("pages").get("restaurant").get(str(res_id)).get("sections").get("SECTION_BASIC_INFO").get("rating_new").get("ratings")
    if rating_data.get("DINING"):
        dining_rating=rating_data.get("DINING").get("rating")
    else:
        dining_rating=None
    if rating_data.get("DELIVERY"):
        delivery_rating=rating_data.get("DELIVERY").get("rating")
    else:
        delivery_rating=None
    opening_hours=data.get("pages").get("restaurant").get(str(res_id)).get("sections").get("SECTION_BASIC_INFO").get("timing").get("customised_timings").get("opening_hours")
    address=data.get("pages").get("restaurant").get(str(res_id)).get("sections").get("SECTION_RES_CONTACT").get("address")
    contact=data.get("pages").get("restaurant").get(str(res_id)).get("sections").get("SECTION_RES_CONTACT").get("phoneDetails").get("phoneStr")
    image_ids = data.get("pages").get("restaurant").get(str(res_id)).get("sections").get('SECTION_IMAGE_CAROUSEL').get('entities')
    main_img_path = data.get('entities').get('IMAGES')
    images = []
    for i in image_ids:
        if i.get('entity_type') == 'IMAGES':
            ids = i.get('entity_ids')
            for id in ids:
                images.append(main_img_path.get(id).get('url'))

    menus=data.get("pages").get("restaurant").get(str(res_id)).get("order").get("menuList").get("menus")
    menu_list=[]
    
    for menu_data in menus:
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

    restaurant_info = {
        "res_id": res_id,
        "res_name": res_name,
        "res_images": images,
        "res_cuisine": res_cuisine,
        "dining_rating": dining_rating,
        "delivery_rating": delivery_rating,
        "opening_hours": opening_hours,
        "address": address,
        "contact": contact,
        "order_online_menu": menu_list
    }
    return restaurant_info

def overview_parser(url):
    json_str = get_page_json(url)
    data= json.loads(json_str)