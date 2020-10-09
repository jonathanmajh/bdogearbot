from fnmatch import fnmatch

from bin.models import GearData, Result


def detect_text(gear_data: GearData):
    """Detects text in the file."""
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    image = vision.types.Image()
    image.source.image_uri = gear_data.scrn_path

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')
    scores_found = 0
    try:
        print(texts[0].description)
    except Exception:
        return Result(False, 'Cannot detect GS please upload a different image')
    split_text = texts[0].description.split('\n')
    for count, text in enumerate(split_text):
        if fnmatch(text, '*Attack*'):
            gear_data.succ_ap = int(split_text[count+1])
            scores_found = scores_found + 1
        if fnmatch(text, '*Awakening*'):
            gear_data.awak_ap = int(split_text[count+1])
            scores_found = scores_found + 1
        if fnmatch(text, '*Defense*'):
            gear_data.dp = int(split_text[count+1])
            scores_found = scores_found + 1

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
