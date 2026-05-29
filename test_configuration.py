#!/usr/bin/env python3
"""
Test script for validating the double saccade trial configuration.
This tests the mathematical correctness without requiring PsychoPy display.
"""

import numpy as np


def create_trial_list(distance=10, repetitions=1):
    """
    Create trial list matching the experiment logic.
    """
    trials = []
    
    # Calculate positions for a square
    d = distance / np.sqrt(2)
    
    # Define the 4 corners of the square
    corners = [
        (d, d),     # top-right (NE)
        (-d, d),    # top-left (NW)
        (-d, -d),   # bottom-left (SW)
        (d, -d)     # bottom-right (SE)
    ]
    
    for i, corner in enumerate(corners):
        x1, y1 = corner
        
        horizontal_target = (-x1, y1)
        vertical_target = (x1, -y1)
        
        trials.append({
            'start_x': 0,
            'start_y': 0,
            'target1_x': x1,
            'target1_y': y1,
            'target2_x': horizontal_target[0],
            'target2_y': horizontal_target[1],
            'first_direction': get_direction_name(x1, y1),
            'second_direction': 'horizontal'
        })
        
        trials.append({
            'start_x': 0,
            'start_y': 0,
            'target1_x': x1,
            'target1_y': y1,
            'target2_x': vertical_target[0],
            'target2_y': vertical_target[1],
            'first_direction': get_direction_name(x1, y1),
            'second_direction': 'vertical'
        })
    
    all_trials = trials * repetitions
    return all_trials


def get_direction_name(x, y):
    """Get cardinal direction name for a position."""
    if x > 0 and y > 0:
        return 'NE'
    elif x < 0 and y > 0:
        return 'NW'
    elif x < 0 and y < 0:
        return 'SW'
    elif x > 0 and y < 0:
        return 'SE'
    return 'center'


def test_square_formation():
    """Test that all targets form a perfect square."""
    print("=" * 60)
    print("Test 1: Square Formation")
    print("=" * 60)
    
    trials = create_trial_list(distance=10, repetitions=1)
    
    # Collect all unique positions
    positions = set()
    for trial in trials:
        positions.add((trial['target1_x'], trial['target1_y']))
        positions.add((trial['target2_x'], trial['target2_y']))
    
    positions = list(positions)
    positions.sort()
    
    print(f"\nUnique target positions: {len(positions)}")
    for pos in positions:
        print(f"  ({pos[0]:.2f}, {pos[1]:.2f})")
    
    # Verify we have exactly 4 positions (corners of square)
    assert len(positions) == 4, f"Expected 4 positions, got {len(positions)}"
    
    # Verify all positions are equidistant from origin
    distances = [np.sqrt(x**2 + y**2) for x, y in positions]
    assert np.allclose(distances, distances[0]), "Not all positions equidistant from center"
    
    print(f"\n✓ All positions equidistant from center: {distances[0]:.2f} deg")
    print("✓ Square formation verified!")


def test_diagonal_first_saccade():
    """Test that first saccades are perfect diagonals."""
    print("\n" + "=" * 60)
    print("Test 2: First Saccade is Diagonal")
    print("=" * 60)
    
    trials = create_trial_list(distance=10, repetitions=1)
    
    print("\nFirst saccade directions:")
    for trial in trials:
        x1, y1 = trial['target1_x'], trial['target1_y']
        
        # Check if it's a perfect diagonal (45 degrees)
        assert abs(abs(x1) - abs(y1)) < 1e-10, f"Not a perfect diagonal: ({x1}, {y1})"
        
        angle = np.arctan2(y1, x1) * 180 / np.pi
        print(f"  {trial['first_direction']}: ({x1:.2f}, {y1:.2f}) -> {angle:.1f}°")
    
    print("\n✓ All first saccades are perfect diagonals (45° from axes)!")


def test_second_saccade_hv():
    """Test that second saccades are horizontal or vertical."""
    print("\n" + "=" * 60)
    print("Test 3: Second Saccade is Horizontal or Vertical")
    print("=" * 60)
    
    trials = create_trial_list(distance=10, repetitions=1)
    
    print("\nSecond saccade directions:")
    for trial in trials:
        x1, y1 = trial['target1_x'], trial['target1_y']
        x2, y2 = trial['target2_x'], trial['target2_y']
        
        # Check if second saccade is horizontal or vertical
        dx = x2 - x1
        dy = y2 - y1
        
        is_horizontal = abs(dy) < 1e-10
        is_vertical = abs(dx) < 1e-10
        
        assert is_horizontal or is_vertical, f"Second saccade neither H nor V: ({dx}, {dy})"
        
        direction = "horizontal" if is_horizontal else "vertical"
        print(f"  {trial['first_direction']} -> {direction}: "
              f"({x1:.2f}, {y1:.2f}) -> ({x2:.2f}, {y2:.2f})")
        
        assert direction == trial['second_direction'], "Direction label mismatch"
    
    print("\n✓ All second saccades are horizontal or vertical!")


def test_equal_second_saccade_length():
    """Test that all second saccades have equal length."""
    print("\n" + "=" * 60)
    print("Test 4: Equal Length of Second Saccades")
    print("=" * 60)
    
    trials = create_trial_list(distance=10, repetitions=1)
    
    lengths = []
    print("\nSecond saccade lengths:")
    for trial in trials:
        x1, y1 = trial['target1_x'], trial['target1_y']
        x2, y2 = trial['target2_x'], trial['target2_y']
        
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        lengths.append(length)
        
        print(f"  {trial['first_direction']} -> {trial['second_direction']}: {length:.2f} deg")
    
    # All lengths should be equal
    assert np.allclose(lengths, lengths[0]), "Second saccades have different lengths"
    
    print(f"\n✓ All second saccades have equal length: {lengths[0]:.2f} deg!")


def test_endpoints_as_startpoints():
    """Test that endpoints can serve as starting points in other trials."""
    print("\n" + "=" * 60)
    print("Test 5: Endpoints as Starting Points")
    print("=" * 60)
    
    trials = create_trial_list(distance=10, repetitions=1)
    
    # Collect all first targets (starting points after initial fixation)
    first_targets = set()
    for trial in trials:
        first_targets.add((trial['target1_x'], trial['target1_y']))
    
    # Collect all second targets (endpoints)
    second_targets = set()
    for trial in trials:
        second_targets.add((trial['target2_x'], trial['target2_y']))
    
    print(f"\nFirst targets (starting points): {len(first_targets)}")
    print(f"Second targets (endpoints): {len(second_targets)}")
    
    # They should be the same set (all corners)
    assert first_targets == second_targets, "Endpoints don't match starting points"
    
    print("\n✓ All endpoints can serve as starting points in other trials!")
    print("✓ Perfect square configuration confirmed!")


def test_trial_count():
    """Test that we have the correct number of trials."""
    print("\n" + "=" * 60)
    print("Test 6: Trial Count")
    print("=" * 60)
    
    repetitions = 5
    trials = create_trial_list(distance=10, repetitions=repetitions)
    
    # 4 diagonal directions × 2 second saccade directions × repetitions
    expected = 4 * 2 * repetitions
    
    print(f"\nExpected trials: {expected}")
    print(f"Actual trials: {len(trials)}")
    
    assert len(trials) == expected, f"Expected {expected} trials, got {len(trials)}"
    
    print("\n✓ Correct number of trials!")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("DOUBLE SACCADE EXPERIMENT - CONFIGURATION TESTS")
    print("=" * 60)
    
    try:
        test_square_formation()
        test_diagonal_first_saccade()
        test_second_saccade_hv()
        test_equal_second_saccade_length()
        test_endpoints_as_startpoints()
        test_trial_count()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nThe experiment configuration is mathematically correct:")
        print("  • 4 targets form a perfect square")
        print("  • First saccades are diagonal (45°)")
        print("  • Second saccades are horizontal or vertical")
        print("  • All second saccades have equal length")
        print("  • Endpoints can serve as starting points")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

