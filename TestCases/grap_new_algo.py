import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

# Set style - using a modern dark style
plt.style.use('dark_background')

# Custom colors
CLOUD_ONPREM_COLOR = '#00bfff'  # Deep sky blue
CLOUD_ONLY_COLOR = '#00ff9d'    # Bright mint green
BG_COLOR = '#1a1a1a'           # Dark grey background
TEXT_COLOR = '#ffffff'         # White text
GRID_COLOR = '#333333'         # Dark grey for grid

# Data for decrypt tests
decrypt_metrics = ['Total\nDuration', 'Requests\nper sec', 'Average\nDuration', 'Median\nDuration', 'Min\nDuration', 'Max\nDuration']
decrypt_cloud_onprem = [10.09, 9.91, 0.97, 0.79, 0.44, 2.30]  # From decrypt_test_results_20241227_225025.json
decrypt_cloud_only = [2.04, 49.09, 0.20, 0.17, 0.13, 0.35]    # From decrypt_test_results_20241227_220517.json

# Data for encrypt tests
encrypt_metrics = ['Total\nDuration', 'Requests\nper sec', 'Average\nDuration', 'Median\nDuration', 'Min\nDuration', 'Max\nDuration']
encrypt_cloud_onprem = [18.43, 5.43, 1.79, 1.52, 0.67, 4.24]  # From encrypt_load_test_results_20241227_224133.json
encrypt_cloud_only = [15.92, 6.28, 1.54, 1.46, 0.57, 3.00]    # From encrypt_test_results_20241227_220042.json

# Create figure with two subplots side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
fig.patch.set_facecolor(BG_COLOR)

# Add a title to the entire figure
fig.suptitle('X25519+ChaCha20-Poly1305: Cloud vs Cloud+OnPremise Performance Analysis', 
             fontsize=16, 
             fontweight='bold',
             color=TEXT_COLOR,
             y=1)

def create_comparison_plot(ax, metrics, cloud_onprem, cloud_only, title):
    x = np.arange(len(metrics))
    width = 0.35
    
    # Add bars with enhanced styling
    bars1 = ax.bar(x - width/2, cloud_onprem, width, label='Cloud+OnPremise', 
                  color=CLOUD_ONPREM_COLOR, alpha=0.9,
                  edgecolor='white', linewidth=1.5)
    bars2 = ax.bar(x + width/2, cloud_only, width, label='Cloud-only',
                  color=CLOUD_ONLY_COLOR, alpha=0.9,
                  edgecolor='white', linewidth=1.5)
    
    # Customize subplot
    ax.set_ylabel('Seconds / Requests per Second', color=TEXT_COLOR, fontsize=12)
    
    # Main title with explanation
    ax.set_title(title + '\n' + 
                 'Higher is better: Requests/sec\nLower is better: All Duration metrics', 
                 pad=20, color=TEXT_COLOR, fontsize=14, fontweight='bold')
    
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, color=TEXT_COLOR, fontsize=10)
    ax.tick_params(colors=TEXT_COLOR)
    ax.grid(True, alpha=0.3, color=GRID_COLOR)
    
    # Add value labels on the bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}',
                       xy=(rect.get_x() + rect.get_width() / 2, height),
                       xytext=(0, 3),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom',
                       color=TEXT_COLOR, fontsize=9)
    
    autolabel(bars1)
    autolabel(bars2)
    
    # Customize legend
    ax.legend(loc='upper right', facecolor=BG_COLOR, edgecolor=TEXT_COLOR)

# Create comparison plots
create_comparison_plot(ax1, encrypt_metrics, 
                      encrypt_cloud_onprem, encrypt_cloud_only,
                      'Encryption Operation Performance')

create_comparison_plot(ax2, decrypt_metrics, 
                      decrypt_cloud_onprem, decrypt_cloud_only,
                      'Decryption Operation Performance')

# Adjust layout
plt.tight_layout()

# Save the plot with high DPI
plt.savefig('x25519_chacha_poly_performance_comparison.png', 
            dpi=300, 
            bbox_inches='tight',
            facecolor=BG_COLOR)
plt.close()