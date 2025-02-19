import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

plt.style.use('dark_background')


CLOUD_ONPREM_COLOR = '#00bfff'
CLOUD_ONLY_COLOR = '#00ff9d' 
BG_COLOR = '#1a1a1a' 
TEXT_COLOR = '#ffffff'
GRID_COLOR = '#333333'    

# Data for decrypt tests
decrypt_metrics = ['Total\nDuration', 'Requests\nper sec', 'Average\nDuration', 'Median\nDuration', 'Min\nDuration', 'Max\nDuration']


decrypt_cloud_onprem = [99.37059211730957, 10.063339451771345, 9.595656961202621, 9.76, 1.7142291069030762, 12.992579221725464]


decrypt_cloud_only = [88.50052618980408, 11.299367846190359, 8.565438908338546, 8.69, 1.1668150424957275, 10.899847984313965]

# Data for encrypt tests
encrypt_metrics = ['Total\nDuration', 'Requests\nper sec', 'Average\nDuration', 'Median\nDuration', 'Min\nDuration', 'Max\nDuration']


encrypt_cloud_onprem = [207.39154267311096, 4.821797394005563, 20.047717767715454, 20.51, 3.7154176235198975, 25.380581855773926]


encrypt_cloud_only = [175.22614669799805, 5.706910862586611, 16.942836599349974, 17.26, 3.690986394882202, 21.182495832443237] 


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
fig.patch.set_facecolor(BG_COLOR)


fig.suptitle('RSA (2048): Cloud vs Cloud+OnPremise Performance Analysis (1000 Requests Testcase with concurrent users 100)', 
             fontsize=16, 
             fontweight='bold',
             color=TEXT_COLOR,
             y=1)

def create_comparison_plot(ax, metrics, cloud_onprem, cloud_only, title):
    x = np.arange(len(metrics))
    width = 0.35
    
    
    bars1 = ax.bar(x - width/2, cloud_onprem, width, label='Cloud+OnPremise', 
                  color=CLOUD_ONPREM_COLOR, alpha=0.9,
                  edgecolor='white', linewidth=1.5)
    bars2 = ax.bar(x + width/2, cloud_only, width, label='Cloud-only',
                  color=CLOUD_ONLY_COLOR, alpha=0.9,
                  edgecolor='white', linewidth=1.5)
    
    
    ax.set_ylabel('Seconds / Requests per Second', color=TEXT_COLOR, fontsize=12)
    
    
    ax.set_title(title + '\n' + 
                 'Higher is better: Requests/sec\nLower is better: All Duration metrics', 
                 pad=20, color=TEXT_COLOR, fontsize=14, fontweight='bold')
    
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, color=TEXT_COLOR, fontsize=10)
    ax.tick_params(colors=TEXT_COLOR)
    ax.grid(True, alpha=0.3, color=GRID_COLOR)
    
    
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
    
   
    ax.legend(loc='upper right', facecolor=BG_COLOR, edgecolor=TEXT_COLOR)


create_comparison_plot(ax1, encrypt_metrics, 
                      encrypt_cloud_onprem, encrypt_cloud_only,
                      'Encryption Operation Performance')

create_comparison_plot(ax2, decrypt_metrics, 
                      decrypt_cloud_onprem, decrypt_cloud_only,
                      'Decryption Operation Performance')


plt.tight_layout()


plt.savefig('x25519_chacha_poly_performance_comparison.png', 
            dpi=300, 
            bbox_inches='tight',
            facecolor=BG_COLOR)
plt.close()