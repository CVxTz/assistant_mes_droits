from assistant_mes_droits.data_processing.download import download_zip
from assistant_mes_droits.data_processing.parse import parse_zip_content


def process_publications():
    zip_data = download_zip(
        "https://lecomarquage.service-public.fr/vdd/3.4/part/zip/vosdroits-latest.zip"
    )
    return parse_zip_content(zip_data)


if __name__ == "__main__":
    _publications = process_publications()

    for _pub in _publications:
        if _pub.id == "F78":
            print(_pub)
