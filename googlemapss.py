import geocoder

def get_current_location():
    g = geocoder.ip('me')  
    if g.latlng:
        return g.latlng 
    else:
        return None

def generate_maps_link(destination):
    source = get_current_location()
    if source:
        source_str = f"{source[0]},{source[1]}"
        maps_url = f"https://www.google.com/maps/dir/{source_str}/{destination.replace(' ', '+')}"
        return maps_url
    else:
        return "https://www.google.com/maps/search/" + destination.replace(' ', '+')

# Example usage
destination = "HBTU Kanpur Uttar Pradesh"
generate_maps_link(destination)
