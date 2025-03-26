import geocoder

def get_current_location():
    g = geocoder.ip('me')  
    if g.latlng:
        return g.latlng 
    else:
        return None

def generate_maps_link(starting_address, address):
    """
    Generate Google Maps directions URL from starting point to destination
    
    Args:
        starting_location: String or coordinates for starting location
        destination: String address of the destination
        
    Returns:
        URL string for Google Maps directions
    """
    # If starting_location is provided, use it
    if starting_address and starting_address.strip():
        # Format the starting location for URL
        source_str = starting_address.replace(' ', '+')
        maps_url = f"https://www.google.com/maps/dir/{source_str}/{address.replace(' ', '+')}"
        return maps_url
    else:
        # If no starting location provided, try using IP-based location
        source = get_current_location()
        if source:
            source_str = f"{source[0]},{source[1]}"
            maps_url = f"https://www.google.com/maps/dir/{source_str}/{address.replace(' ', '+')}"
            return maps_url
        else:
            # Fallback to just searching for the destination
            return "https://www.google.com/maps/search/" + address.replace(' ', '+')

# Example usage
destination = "HBTU Kanpur Uttar Pradesh"
generate_maps_link(None, destination)