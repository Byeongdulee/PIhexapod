"""
Test script for the analyze_pulse_steps function
This demonstrates the function logic with manual calculation
"""

# Sample data from the user's example
pulse_positions_index = [25, 125, 225, 325, 425, 525, 625, 725, 825, 925, 1025, 1075, 
                         1175, 1275, 1375, 1475, 1575, 1675, 1775, 1875, 1975, 2075, 
                         2125, 2225, 2325, 2425, 2525, 2625, 2725, 2825, 2925, 3025, 
                         3125, 3175, 3275, 3375, 3475, 3575, 3675, 3775, 3875, 3975, 
                         4075, 4175, 4225, 4325, 4425, 4525, 4625, 4725, 4825, 4925, 
                         5025, 5125, 5225, 5275, 5375, 5475, 5575, 5675, 5775, 5875, 
                         5975, 6075, 6175, 6275, 6325, 6425, 6525, 6625, 6725, 6825, 
                         6925, 7025, 7125, 7225, 7325, 7375]

print(f"Pulse positions count: {len(pulse_positions_index)}")
print(f"Example pulse positions: {pulse_positions_index[:15]}")

# Calculate differences between consecutive elements
steps = [pulse_positions_index[i+1] - pulse_positions_index[i] 
         for i in range(len(pulse_positions_index) - 1)]

print(f"\nFirst 15 steps: {steps[:15]}")

# Find minimum step
min_step = min(steps)
print(f"\nMinimum step: {min_step}")

# Count each step value
step_counts = {}
for step in steps:
    step_counts[step] = step_counts.get(step, 0) + 1

# Find most common step
most_common_step = max(step_counts, key=step_counts.get)
print(f"Most common step: {most_common_step}")

print(f"\nStep distribution:")
for step in sorted(step_counts.keys()):
    count = step_counts[step]
    print(f"  Step {step}: appears {count} times")

print(f"\n✓ The analyze_pulse_steps() function would return: ({min_step}, {most_common_step})")
