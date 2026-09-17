import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# IEEE Publication Standards
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--'
})

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, '../benchmarks/data')
FIG_DIR = BASE_DIR

def plot_proof_latency():
    df = pd.read_csv(os.path.join(DATA_DIR, 'client_proof_latency.csv'))
    
    fig, ax1 = plt.subplots(figsize=(6, 4))
    
    color1 = '#1f77b4'
    ax1.set_xlabel('Merkle Tree Depth (log$_2$(N))')
    ax1.set_ylabel('Proving Time (ms)', color=color1)
    ax1.plot(df['tree_depth'], df['proof_gen_time_ms'], marker='o', color=color1, linewidth=2, label='Proving Time')
    ax1.tick_params(axis='y', labelcolor=color1)
    
    ax2 = ax1.twinx()
    color2 = '#ff7f0e'
    ax2.set_ylabel('Peak RAM Usage (MB)', color=color2)
    ax2.plot(df['tree_depth'], df['peak_ram_mb'], marker='s', color=color2, linewidth=2, linestyle='--', label='RAM Usage')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    plt.title('Zk-Vote Client-Side Proving Overhead')
    fig.tight_layout()
    
    plt.savefig(os.path.join(FIG_DIR, 'figure_1_proof_latency.pdf'), format='pdf', bbox_inches='tight')
    plt.savefig(os.path.join(FIG_DIR, 'figure_1_proof_latency.png'), format='png', bbox_inches='tight')
    plt.close()
    print("Generated Figure 1: Proof Latency")

def plot_cairo_breakdown():
    df = pd.read_csv(os.path.join(DATA_DIR, 'cairo_step_breakdown.csv'))
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Sort for better visual hierarchy
    df = df.sort_values('percentage', ascending=True)
    
    bars = ax.barh(df['operation'], df['percentage'], color=sns.color_palette("Blues_d", len(df)))
    
    ax.set_xlabel('Percentage of Total Cairo Execution Steps (%)')
    ax.set_title('On-Chain Verification Resource Allocation')
    
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{width:.1f}%',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(3, 0),  # 3 points horizontal offset
                    textcoords="offset points",
                    ha='left', va='center')

    fig.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'figure_2_cairo_resource_breakdown.pdf'), format='pdf', bbox_inches='tight')
    plt.savefig(os.path.join(FIG_DIR, 'figure_2_cairo_resource_breakdown.png'), format='png', bbox_inches='tight')
    plt.close()
    print("Generated Figure 2: Cairo Breakdown")

def plot_cost_comparison():
    df = pd.read_csv(os.path.join(DATA_DIR, 'l2_cost_comparison.csv'))
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    x = np.arange(len(df['platform']))
    width = 0.35
    
    gas_costs = df['gas_cost_usd']
    amortized_costs = df['amortized_cost_usd']
    
    ax.bar(x - width/2, gas_costs, width, label='Single Tx Cost ($)', color='#2ca02c')
    ax.bar(x + width/2, amortized_costs, width, label='Amortized Cost (Batched) ($)', color='#9467bd')
    
    ax.set_ylabel('Cost (USD) - Log Scale')
    ax.set_title('Transaction Cost Comparison: L2 Starknet vs L1 Ethereum')
    ax.set_xticks(x)
    ax.set_xticklabels(df['platform'])
    ax.set_yscale('log')
    ax.legend()
    
    fig.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'figure_3_cost_comparison.pdf'), format='pdf', bbox_inches='tight')
    plt.savefig(os.path.join(FIG_DIR, 'figure_3_cost_comparison.png'), format='png', bbox_inches='tight')
    plt.close()
    print("Generated Figure 3: Cost Comparison")

if __name__ == "__main__":
    plot_proof_latency()
    plot_cairo_breakdown()
    plot_cost_comparison()
