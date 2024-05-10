def maps_url_composer(lat, long):
    if not -90 <= lat <= 90:
        raise ValueError("Invalid latitude: must be between -90 and 90.")
    if not -180 <= long <= 180:
        raise ValueError("Invalid longitude: must be between -180 and 180.")

    return f"https://www.google.com/maps/place/{lat},{long}"


def link(uri, label=None):
    if label is None:
        label = uri
    parameters = ''

    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'

    return escape_mask.format(parameters, uri, label)
