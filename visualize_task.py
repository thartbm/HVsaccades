#!/usr/bin/env python3
"""
Visualization script to demonstrate the double saccade task configuration.
Creates a diagram showing all possible saccade paths.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch
import matplotlib.patches as mpatches


def visualize_task(distance=10):
    """
    Create a visualization of the double saccade task.
    
    Args:
        distance: Distance from center to each target
    """
    # Calculate corner positions
    d = distance / np.sqrt(2)
    corners = {
        'NE': (d, d),
        'NW': (-d, d),
        'SW': (-d, -d),
        'SE': (d, -d)
    }
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot 1: All first saccades (diagonal)
    ax1.set_xlim(-d-2, d+2)
    ax1.set_ylim(-d-2, d+2)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='k', linestyle='-', alpha=0.2)
    ax1.axvline(x=0, color='k', linestyle='-', alpha=0.2)
    ax1.set_title('First Saccades (Diagonal)', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Horizontal Position (deg)', fontsize=12)
    ax1.set_ylabel('Vertical Position (deg)', fontsize=12)
    
    # Draw fixation point
    ax1.plot(0, 0, 'o', color='white', markersize=15, 
             markeredgecolor='black', markeredgewidth=2, label='Fixation')
    
    # Draw first saccades (diagonal from center to each corner)
    colors = {'NE': 'red', 'NW': 'blue', 'SW': 'green', 'SE': 'orange'}
    for name, (x, y) in corners.items():
        arrow = FancyArrowPatch((0, 0), (x, y),
                               arrowstyle='->', mutation_scale=20,
                               linewidth=2, color=colors[name],
                               label=f'{name} (1st)')
        ax1.add_patch(arrow)
        ax1.plot(x, y, 'o', color=colors[name], markersize=20,
                markeredgecolor='black', markeredgewidth=2)
        ax1.text(x*1.15, y*1.15, name, fontsize=14, fontweight='bold',
                ha='center', va='center')
    
    ax1.legend(loc='upper left', fontsize=10)
    
    # Plot 2: All second saccades (horizontal and vertical)
    ax2.set_xlim(-d-2, d+2)
    ax2.set_ylim(-d-2, d+2)
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='k', linestyle='-', alpha=0.2)
    ax2.axvline(x=0, color='k', linestyle='-', alpha=0.2)
    ax2.set_title('Second Saccades (Horizontal & Vertical)', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Horizontal Position (deg)', fontsize=12)
    ax2.set_ylabel('Vertical Position (deg)', fontsize=12)
    
    # Draw all corners
    for name, (x, y) in corners.items():
        ax2.plot(x, y, 'o', color='gray', markersize=20,
                markeredgecolor='black', markeredgewidth=2, alpha=0.5)
        ax2.text(x*1.15, y*1.15, name, fontsize=14, fontweight='bold',
                ha='center', va='center')
    
    # Draw second saccades from each corner
    for name, (x1, y1) in corners.items():
        # Horizontal second saccade
        x2_h, y2_h = -x1, y1
        arrow_h = FancyArrowPatch((x1, y1), (x2_h, y2_h),
                                 arrowstyle='->', mutation_scale=15,
                                 linewidth=2, color='purple',
                                 linestyle='-', alpha=0.7)
        ax2.add_patch(arrow_h)
        
        # Vertical second saccade
        x2_v, y2_v = x1, -y1
        arrow_v = FancyArrowPatch((x1, y1), (x2_v, y2_v),
                                 arrowstyle='->', mutation_scale=15,
                                 linewidth=2, color='darkgreen',
                                 linestyle='--', alpha=0.7)
        ax2.add_patch(arrow_v)
    
    # Add legend
    h_patch = mpatches.Patch(color='purple', label='Horizontal 2nd saccade')
    v_patch = mpatches.Patch(color='darkgreen', label='Vertical 2nd saccade')
    ax2.legend(handles=[h_patch, v_patch], loc='upper left', fontsize=10)
    
    # Add overall title
    fig.suptitle('Double Saccade Task Configuration', fontsize=18, fontweight='bold', y=0.98)
    
    # Add text explanation
    fig.text(0.5, 0.02, 
             'Left: First saccade is diagonal (45°) to one of 4 corners\n'
             'Right: Second saccade is horizontal (solid) or vertical (dashed) to an adjacent corner\n'
             'All 4 targets form a perfect square | All second saccades have equal length',
             ha='center', fontsize=11, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    
    # Save figure
    output_file = 'task_visualization.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Visualization saved to {output_file}")
    
    plt.show()


if __name__ == '__main__':
    visualize_task(distance=10)
