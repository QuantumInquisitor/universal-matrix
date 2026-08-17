import sys
import ssl
import urllib.request
import math
from skyfield.api import load, Topos, EarthSatellite

# Direct link interface hook to your telemetry module
try:
    from src.data_logger import log_metric
except ImportError:
    # Safe fall-through logger framework if local file paths are decoupled
    def log_metric(category, message):
        print(f"📊 [TELEMETRY_STREAM] {category.upper()}: {message}")

def compute_hypercube_gate_projections(lat, lon):
    """
    Maps 2D geodetic surface coordinates across the 6 boundary face gates
    of the 114-node multi-dimensional system architecture framework.
    """
    rad_lat = math.radians(lat)
    rad_lon = math.radians(lon)
    
    # Calculate geometric projection boundary face parameters
    x = math.cos(rad_lat) * math.cos(rad_lon)
    y = math.cos(rad_lat) * math.sin(rad_lon)
    z = math.sin(rad_lat)
    
    # Calculate dimensional weights across the 6 boundary intersections
    gate_flux_vectors = [
        abs(x) if x >= 0 else 0,  # Gate 1: Positive X Axis
        abs(x) if x < 0 else 0,   # Gate 2: Negative X Axis
        abs(y) if y >= 0 else 0,  # Gate 3: Positive Y Axis
        abs(y) if y < 0 else 0,   # Gate 4: Negative Y Axis
        abs(z) if z >= 0 else 0,  # Gate 5: Positive Z Axis
        abs(z) if z < 0 else 0    # Gate 6: Negative Z Axis
    ]
    return gate_flux_vectors

def fetch_and_find_closest_starlink():
    print("📡 Initializing Unified Telemetry Intercept and Matrix Alignment System...")
    
    # Highly robust community mirror providing stable, raw unthrottled aerospace data sets
    tle_url = 'https://githubusercontent.com'
    local_filename = 'starlink.tle'
    
    context = ssl._create_unverified_context()
    req = urllib.request.Request(
        tle_url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    
    try:
        with urllib.request.urlopen(req, context=context) as response:
            data = response.read()
            with open(local_filename, 'wb') as out_file:
                out_file.write(data)
        print("📥 Live orbital parameters successfully downloaded and cached locally.")
    except Exception as e:
        print(f"❌ Core Telemetry Connection Aborted: {e}")
        print("💡 Informational: System will run via pipeline framework when internet route goes live.")
        sys.exit(1)

    try:
        satellites = load.tle_file(local_filename)
        if not satellites:
            raise ValueError("Parsed file array evaluates to zero elements.")
        print(f"✅ Successfully initialized {len(satellites)} live orbital vector paths.")
    except Exception as e:
        print(f"❌ Matrix Parser Fault: {e}")
        sys.exit(1)

    ts = load.timescale()
    current_time = ts.now()

    # System Reference Box Coordinates (Austin, TX Node Matrix Anchor Point)
    workspace_lat, workspace_lon = '30.2672 N', '97.7431 W'
    local_observer = Topos(workspace_lat, workspace_lon)
    
    closest_sat = None
    min_distance_km = float('inf')
    overhead_count = 0

    print("🔍 Propagating orbital nodes across local coordinate limits...")
    for sat in satellites:
        try:
            difference = sat - local_observer
            topocentric = difference.at(current_time)
            alt, az, distance = topocentric.altaz()
            
            if alt.degrees > 0:
                overhead_count += 1
                
            if distance.km < min_distance_km:
                min_distance_km = distance.km
                closest_sat = (sat, alt.degrees, az.degrees)
        except Exception:
            continue

    if closest_sat:
        target, target_alt, target_az = closest_sat
        geocentric_pos = target.at(current_time)
        subpoint = geocentric_pos.subpoint()
        
        target_lat = subpoint.latitude.degrees
        target_lon = subpoint.longitude.degrees
        target_alt_km = subpoint.elevation.km
        
        # Calculate real mathematical gate distributions
        gate_flux = compute_hypercube_gate_projections(target_lat, target_lon)
        
        print("=" * 60)
        print(f"🎯 NEAREST SPACE-X ORBITAL CORE BALANCED:")
        print(f"🛰️ Satellite Identifier:  {target.name}")
        print(f"🔢 Catalog Reference ID: {target.model.satnum}")
        print(f"📡 Vector Slant Range:   {min_distance_km:.2f} km")
        print(f"📍 Sub-Point Coordinate:  {target_lat:.4f}° N, {target_lon:.4f}° W")
        print("=" * 60)
        
        # Pipe operations into data_logger telemetry loop fields
        log_metric("satellite_id", f"{target.name} (NORAD: {target.model.satnum})")
        log_metric("slant_range_km", f"{min_distance_km:.4f}")
        log_metric("geodetic_position", f"lat:{target_lat:.4f}, lon:{target_lon:.4f}, alt:{target_alt_km:.2f}")
        log_metric("overhead_count", f"{overhead_count}")
        
        # Distribute calculated metrics across the 6 hypercube boundary face vectors
        for idx, scalar in enumerate(gate_flux, start=1):
            log_metric(f"hypercube_gate_{idx}_flux", f"{scalar:.8f}")
            
        print("\n✅ System Intercept Complete. Metrics pushed to local telemetry pipeline arrays.")
    else:
        print("❌ Analytics validation failure: Unable to converge coordinate targets.")

if __name__ == "__main__":
    fetch_and_find_closest_starlink()
