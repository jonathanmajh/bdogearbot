from fnmatch import fnmatch

from bin.models import GearData, Result

def same_line(text1, text2):
    """check if text is somewhat on the same line"""
    box1y = text1.bounding_poly.vertices[1].y + text1.bounding_poly.vertices[2].y
    box2y = text2.bounding_poly.vertices[1].y + text2.bounding_poly.vertices[2].y
    if abs(box1y - box2y) < 10:
        return True
    return False

def detect_text(gear_data: GearData):
    """Detects text in the file."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    image = vision.Image(content=gear_data.obj)

    # image = vision.types.Image()
    # image.source.image_uri = gear_data.scrn_path

    response = client.text_detection(image=image)
    texts = response.text_annotations
    scores_found = 0
    if response.error.message:
        return Result(False, f'Error encountered: {response.error.message}')
    # split_text = texts[0].description.split('\n')
    print('Removing from stack:')
    print(texts.pop(0))
    for count, text in enumerate(texts):
        print(text.description)
        if fnmatch(text.description, '*Attack*'):
            for j in range(count, len(texts)):
                if texts[j].description.isnumeric() & same_line(text, texts[j]):
                    gear_data.succ_ap = int(texts[j].description)
                    print(f'Found Succ AP: ${texts.pop(j)}')
                    scores_found = scores_found + 1
                    break
        if fnmatch(text.description, '*Awakening*'):
            for j in range(count, len(texts)):
                if texts[j].description.isnumeric() & same_line(text, texts[j]):
                    gear_data.awak_ap = int(texts[j].description)
                    print(f'Found Awak AP: ${texts.pop(j)}')
                    scores_found = scores_found + 1
                    break
        if fnmatch(text.description, '*Talent*'):
            for j in range(count, len(texts)):
                if texts[j].description.isnumeric() & same_line(text, texts[j]):
                    gear_data.awak_ap = int(texts[j].description)
                    print(f'Found Awak AP: ${texts.pop(j)}')
                    scores_found = scores_found + 1
                    break
        if fnmatch(text.description, '*Defense*'):
            for j in range(count, len(texts)):
                if texts[j].description.isnumeric() & same_line(text, texts[j]):
                    gear_data.dp = int(texts[j].description)
                    print(f'Found DP: ${texts.pop(j)}')
                    scores_found = scores_found + 1
                    break

    if scores_found == 3:
        gear_data.gs = max(gear_data.succ_ap, gear_data.awak_ap) + gear_data.dp
        return Result(True, gear_data=gear_data)
    else:
        return Result(False, 'Cannot detect GS please upload a different image')

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
