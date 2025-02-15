import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

# Set style - using a more modern style
plt.style.use('dark_background')

# Custom colors - Using a color palette optimized for dark background
CLOUD_ONPREM_COLOR = '#00bfff'  # Deep sky blue
CLOUD_ONLY_COLOR = '#00ff9d'    # Bright mint green
BG_COLOR = '#1a1a1a'           # Dark grey background
TEXT_COLOR = '#ffffff'         # White text
GRID_COLOR = '#333333'         # Dark grey for grid

# Data for decrypt tests
decrypt_metrics = ['Total\nDuration', 'Requests\nper sec', 'Average\nDuration', 'Median\nDuration', 'Min\nDuration', 'Max\nDuration']
decrypt_cloud_onprem = [15.05, 6.64, 1.45, 1.33, 0.50, 4.06]
decrypt_cloud_only = [9.27, 10.78, 0.90, 0.77, 0.35, 1.91]

# Data for load tests
load_metrics = ['Total\nDuration', 'Requests\nper sec', 'Average\nDuration', 'Median\nDuration', 'Min\nDuration', 'Max\nDuration']
load_cloud_onprem = [24.15, 4.14, 2.28, 1.79, 0.65, 4.91]
load_cloud_only = [21.26, 4.70, 2.03, 2.24, 0.62, 3.71]

# Create figure with two subplots side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
fig.patch.set_facecolor(BG_COLOR)

# Add a title to the entire figure
fig.suptitle('Cloud vs Cloud+OnPremise Performance Analysis', 
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
    
    # Main title
    ax.set_title(title + '\n' + 
                 'Higher is better: Requests/sec\nLower is better: All Duration metrics', 
                 pad=20, color=TEXT_COLOR, fontsize=14, fontweight='bold')
    
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, color=TEXT_COLOR, fontsize=10)
    ax.tick_params(colors=TEXT_COLOR)
    ax.grid(True, alpha=0.3, color=GRID_COLOR)
    
    # Add value labels on the bars
    def autolabel(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', color=TEXT_COLOR,
                   fontsize=10)
    
    autolabel(bars1)
    autolabel(bars2)
    
    # Customize legend
    ax.legend(loc='upper right', facecolor=BG_COLOR, edgecolor=TEXT_COLOR)

# Create comparison plots
create_comparison_plot(ax2, decrypt_metrics, 
                      decrypt_cloud_onprem, decrypt_cloud_only,
                      'Decrypt Operation Performance')

create_comparison_plot(ax1, load_metrics,
                      load_cloud_onprem, load_cloud_only,
                      'Encryption Operation Performance')

# Adjust layout
plt.tight_layout()

# Save the plot with high DPI
plt.savefig('performance_comparison.png', 
            dpi=300, 
            bbox_inches='tight',
            facecolor=BG_COLOR)
plt.close()