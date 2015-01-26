import requests
import schedule
import time
import ujson

INSTAGRAM_CLIENT_ID = 'd9c8568aba9041ffaf55b3ce1e89456c'

API_ENDPOINT_TAGS = 'https://api.instagram.com/v1/tags/{tag}/media/recent?client_id={client_id}'
# API_ENDPOINT_USERS = 'https://api.instagram.com/v1/users/{user_id}/?client_id={client_id}'

LIKE_REQUIRED_FROM_USER = "195687334"  # _crestina_

SEARCH_TAGS = [
    'aosta',
    'fablab',
]

JSON_EXPORT_FILE = './htdocs/assets/export.json'


def get_recent_photos_with_tag(tag, client_id):
    """Requests recent photos with a precise tag from instagram API, discarding
    all the photos that do not have lat/lon data.

    Returns a list of objects with a structure like this:
    {
        'id': photo ID
        'data': {
            'standard': standard resolution image URL
            'thumbnail': thumbnail image URL
            'low': low resolution image URL
        }
        'user_id': user that published photo (numeric ID)
        'username': user that published photo (username)
        'fullname': user that published photo (real name)
        'time': time the photo was published (millis from epoch)
        'text': caption that the user inserted
        'lat': latitude (if any)
        'lon': longitude (if any)
        'likes': list of user IDs that liked the picture
    }
    """
    url = API_ENDPOINT_TAGS.format(tag=tag, client_id=client_id)

    r = requests.get(url)
    if r.status_code != 200:
        print('Error: HTTP Request <GET(%s)> failed with response code %d.'
              % (url, r.status_code))
        return None

    jresp = r.json()
    if jresp['meta']['code'] != 200:
        print('Error: API Request <%s> failed with status code %d.'
              % (url, jresp['meta']['code']))
        return None

    print('DEBUG: Query for tag <"%s"> returned %d images.'
          % (tag, len(jresp['data'])))

    result = []

    for image in jresp['data']:
        if 'location' not in image:
            print('NOLOC')
            continue
        try:
            image_obj = {
                'id': image['caption']['id'],
                'user_id': image['user']['id'],
                'username': image['user']['username'],
                'fullname': image['user']['full_name'],
                'time': image['caption']['created_time'],
                'text': image['caption']['text'],
                'lat': image['location']['latitude'],
                'lon': image['location']['longitude'],
                'data': {
                    'standard': image['images']['standard_resolution']['url'],
                    'thumbnail': image['images']['thumbnail']['url'],
                    'low': image['images']['low_resolution']['url']
                }
            }

            if 'likes' in image:
                image_obj['likes'] = [x['id'] for x in image['likes']['data']]

            result.append(image_obj)
        except:
            continue

    print('DEBUG: %d images got location information out of %d total.'
          % (len(result), len(jresp['data'])))

    return result


def filter_images_with_like(images, user_id):
    """Takes a list of pictures and removes the ones which do not have likes
    from user identified by `user_id`, returning a new filtered list

    """
    filtered = []

    for image in images:
        if 'likes' not in image:
            continue
        if user_id in image['likes']:
            filtered.append(image)

    print('DEBUG: %d images out of %d got like from user <%s>'
          % (len(filtered), len(images), user_id))

    return filtered


def update_json_file(file_path, images):
    """Updates JSON file with images data preventing duplicates."""
    new_data = []

    with open(file_path, 'r+') as infile:
        old_data = ujson.load(infile)

        print('DEBUG: File <%s> contained %d images'
              % (file_path, len(old_data)))

        for image in images:
            insert = True
            for old_image in old_data:
                if image['id'] == old_image['id']:
                    insert = False
            if insert:
                new_data.append(image)

        print('DEBUG: File <%s> gets updated with %d new images'
              % (file_path, len(new_data)))

        old_data.extend(new_data)

        infile.truncate(0)

        ujson.dump(old_data, infile)


def main():
    images = []

    for tag in SEARCH_TAGS:
        tagimgs = get_recent_photos_with_tag(tag, INSTAGRAM_CLIENT_ID)
        images.extend(tagimgs)

    images = filter_images_with_like(images, LIKE_REQUIRED_FROM_USER)

    export_exists = False
    try:
        open(JSON_EXPORT_FILE)
    except IOError:
        export_exists = False

    if export_exists:
        update_json_file(JSON_EXPORT_FILE, images)
        print('Wrote updated `%s`.' % (JSON_EXPORT_FILE))
    else:
        with open(JSON_EXPORT_FILE, 'w') as outfile:
            ujson.dump(images, outfile)
            print('Wrote NEW `%s`.' % (JSON_EXPORT_FILE))


schedule.every(1).minutes.do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
