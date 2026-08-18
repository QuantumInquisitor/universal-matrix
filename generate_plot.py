import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 10), facecolor='#0F0F1F')
ax.set_facecolor('#0F0F1F')

n_core = 108
theta_core = np.linspace(0, 2 * np.pi, n_core, endpoint=False)
r_core = 1.0
x_core = r_core * np.cos(theta_core)
y_core = r_core * np.sin(theta_core)
ax.scatter(x_core, y_core, color='#00FFCC', alpha=0.6, s=15, label='108-Node Core Matrix', zorder=3)

n_gates = 6
theta_gates = np.linspace(0, 2 * np.pi, n_gates, endpoint=False)
r_gates = 1.4
x_gates = r_gates * np.cos(theta_gates)
y_gates = r_gates * np.sin(theta_gates)
ax.scatter(x_gates, y_gates, color='#FF0055', alpha=0.9, s=80, edgecolors='#FFFFFF', linewidths=1.5, label='6 Outer Hypercube Gates', zorder=5)

for i in range(n_gates):
    for j in range(i + 1, n_gates):
        ax.plot([x_gates[i], x_gates[j]], [y_gates[i], y_gates[j]], color='#FF0055', alpha=0.25, linestyle='-', linewidth=1.2, zorder=2)

step = 21
for i in range(n_core):
    next_node = (i + step) % n_core
    ax.plot([x_core[i], x_core[next_node]], [y_core[i], y_core[next_node]], color='#0066FF', alpha=0.12, linewidth=0.8, zorder=1)

gate_labels = ['G1 (3)', 'G2 (6)', 'G3 (9)', 'G4 (3*)', 'G5 (6*)', 'G6 (9*)']
for i, (x, y) in enumerate(zip(x_gates, y_gates)):
    ax.text(x * 1.08, y * 1.08, gate_labels[i], color='#FFFFFF', fontsize=10, ha='center', va='center', fontweight='bold', bbox=dict(facecolor='#1A1A3A', alpha=0.8, edgecolor='#FF0055', boxstyle='round,pad=0.3'))

ax.set_xlim(-1.7, 1.7)
ax.set_ylim(-1.7, 1.7)
ax.axis('off')
ax.text(0, 1.6, "Figure 2: 114-Node Matrix Geometry Layout", color='#FFFFFF', fontsize=14, fontweight='bold', ha='center')
ax.text(0, -1.6, r"$\alpha_{geometric} = \frac{1}{54\pi^2} \approx 0.090606346384$", color='#8A8AAB', fontsize=11, ha='center', style='italic')
ax.legend(loc='lower left', facecolor='#1A1A3A', edgecolor='#333366', labelcolor='#FFFFFF')
plt.tight_layout()

plt.savefig('figure2_matrix_geometry.png', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
