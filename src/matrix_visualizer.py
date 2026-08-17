import sys
import os
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Ensure local imports work cleanly from the root directory context
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import the projection system directly from your new tracker script
try:
    from satellite_tracker import compute_hypercube_gate_projections
except ImportError:
    # Fallback placeholder if modules are executed outside of source layout
    def compute_hypercube_gate_projections(lat, lon):
        return [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]

def generate_base_matrix_nodes():
    """Generates standard 114-node field coordinate matrix."""
    nodes = []
    for i in range(114):
        # Golden spiral / spherical distribution across the universal grid layout
        phi = math.acos(1 - 2 * (i + 0.5) / 114)
        theta = math.pi * (1 + 5**0.5) * i
        
        x = math.sin(phi) * math.cos(theta)
        y = math.sin(phi) * math.sin(theta)
        z = math.cos(phi)
        nodes.append((x, y, z))
    return nodes

def render_dynamic_field(satellite_coords=None):
    """
    Renders the 114-node matrix layout and injects a prominent orbital 
    vector marker tracking the live position of the nearest satellite.
    """
    print("🎨 Generating 3D Vector Matrix Grid Layout...")
    nodes = generate_base_matrix_nodes()
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. Unpack base node clusters
    xs = [n[0] for n in nodes]
    ys = [n[1] for n in nodes]
    zs = [n[2] for n in nodes]
    
    # Plot standard nodes as royal blue structural anchors
    ax.scatter(xs, ys, zs, c='royalblue', s=20, alpha=0.6, label='114-Node Core Matrix')
    
    # 2. Extract and highlight the 3-6-9 control vectors (Crimson Nodes)
    # Using index subsets representing Tesla node steps
    crimson_xs, crimson_ys, crimson_zs = [], [], []
    for idx in range(0, 114, 3):
        crimson_xs.append(nodes[idx][0])
        crimson_ys.append(nodes[idx][1])
        crimson_zs.append(nodes[idx][2])
    ax.scatter(crimson_xs, crimson_ys, crimson_zs, c='crimson', s=45, alpha=0.9, label='3-6-9 Control Triad')

    # 3. Dynamic Live Satellite Vector Injection
    if satellite_coords:
        lat, lon = satellite_coords
        print(f"🛰️ Projecting tracking coordinates into 3D Vector Space: Lat {lat:.4f}, Lon {lon:.4f}")
        
        # Translate geodetic coordinates to matching 3D matrix space
        rad_lat = math.radians(lat)
        rad_lon = math.radians(lon)
        
        # Scale slightly outside the base sphere radius (1.25) so it floats clearly above the core grid
        sat_x = 1.25 * math.cos(rad_lat) * math.cos(rad_lon)
        sat_y = 1.25 * math.cos(rad_lat) * math.sin(rad_lon)
        sat_z = 1.25 * math.sin(rad_lat)
        
        # Plot the satellite as a large, bright emerald green marker
        ax.scatter([sat_x], [sat_y], [sat_z], c='#00FF66', s=150, marker='*', 
                   edgecolors='black', linewidths=1.5, label='Live Satellite Intercept')
        
        # Draw a targeting vector line from the center of your matrix out to the satellite point
        ax.plot([0, sat_x], [0, sat_y], [0, sat_z], c='#00FF66', linestyle='--', alpha=0.8, linewidth=2)
        
    # Visual Layout Polish
    ax.set_title("Universal Field Engine — Live Orbital Intercept Tracking", fontsize=14, pad=20)
    ax.set_xlabel("X Axis Face Gates")
    ax.set_ylabel("Y Axis Face Gates")
    ax.set_zlabel("Z Axis Face Gates")
    ax.legend(loc='upper right')
    
    # Set uniform bounds to keep geometry crisp and balanced
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_zlim([-1.5, 1.5])
    
    print("📈 Rendering localized UI canvas loops successfully.")
    plt.show()

if __name__ == "__main__":
    # Mocking standard target coordinate loop point if tracking script is offline
    # Example coordinates: Lat 30.2672 (Austin, TX Node anchor boundary point), Lon -97.7431
    active_target_coordinates = (30.2672, -97.7431)
    render_dynamic_field(satellite_coords=active_target_coordinates)
