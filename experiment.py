#!/usr/bin/env python3
"""
Double Saccade Experiment for testing HV illusion effects
Participants make two saccades:
1. First saccade: diagonal (45 degrees) in one of 4 directions
2. Second saccade: horizontal or vertical
All targets form a perfect square configuration.
"""

from psychopy import visual, core, event, gui, data
import numpy as np
import os
from datetime import datetime


class DoubleSaccadeExperiment:
    def __init__(self, participant_id, distance=10, repetitions=5, random_seed=None):
        """
        Initialize the double saccade experiment.
        
        Args:
            participant_id: Participant identifier
            distance: Distance from center to each target in degrees of visual angle
            repetitions: Number of repetitions per condition
            random_seed: Optional random seed for reproducibility
        """
        self.participant_id = participant_id
        self.distance = distance  # distance from center to target
        self.repetitions = repetitions
        self.random_seed = random_seed
        
        # Set random seed if provided
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Create window
        self.win = visual.Window(
            size=[1920, 1080],
            fullscr=True,
            units='deg',
            color='black',
            allowGUI=False
        )
        
        # Create stimuli
        self.fixation = visual.Circle(
            self.win,
            radius=0.2,
            fillColor='white',
            lineColor='white',
            pos=[0, 0]
        )
        
        self.target = visual.Circle(
            self.win,
            radius=0.3,
            fillColor='red',
            lineColor='red'
        )
        
        # Setup data directory
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Setup trial list
        self.trials = self._create_trial_list()
        
        # Create experiment handler
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.data_dir}/{self.participant_id}_{timestamp}"
        self.exp_handler = data.ExperimentHandler(
            name='DoubleSaccade',
            version='1.0',
            extraInfo={'participant': participant_id},
            dataFileName=filename
        )
        
    def _create_trial_list(self):
        """
        Create a list of trials with all possible combinations.
        
        For a perfect square configuration:
        - 4 corner positions (diagonal from center)
        - From each corner, 2 possible second saccades (H or V)
        - This creates 8 unique conditions
        """
        trials = []
        
        # Calculate positions for a square
        # Using diagonal distance from center
        d = self.distance / np.sqrt(2)  # distance along each axis
        
        # Define the 4 corners of the square
        corners = [
            (d, d),     # top-right (NE)
            (-d, d),    # top-left (NW)
            (-d, -d),   # bottom-left (SW)
            (d, -d)     # bottom-right (SE)
        ]
        
        # For each corner as starting point
        for i, corner in enumerate(corners):
            x1, y1 = corner
            
            # Find the two adjacent corners (horizontal and vertical neighbors)
            # For a square, each corner has 2 neighbors
            # Horizontal neighbor: same y, opposite x
            # Vertical neighbor: same x, opposite y
            
            horizontal_target = (-x1, y1)  # flip x coordinate
            vertical_target = (x1, -y1)    # flip y coordinate
            
            # Create trial for horizontal second saccade
            trials.append({
                'start_x': 0,
                'start_y': 0,
                'target1_x': x1,
                'target1_y': y1,
                'target2_x': horizontal_target[0],
                'target2_y': horizontal_target[1],
                'first_direction': self._get_direction_name(x1, y1),
                'second_direction': 'horizontal'
            })
            
            # Create trial for vertical second saccade
            trials.append({
                'start_x': 0,
                'start_y': 0,
                'target1_x': x1,
                'target1_y': y1,
                'target2_x': vertical_target[0],
                'target2_y': vertical_target[1],
                'first_direction': self._get_direction_name(x1, y1),
                'second_direction': 'vertical'
            })
        
        # Replicate trials based on repetitions
        all_trials = trials * self.repetitions
        
        # Randomize trial order
        np.random.shuffle(all_trials)
        
        return all_trials
    
    def _get_direction_name(self, x, y):
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
    
    def show_instructions(self):
        """Display experiment instructions."""
        instructions = visual.TextStim(
            self.win,
            text="""Welcome to the Double Saccade Experiment!
            
In this experiment, you will see a series of targets.
Your task is to follow the targets with your eyes as quickly and accurately as possible.

Each trial will proceed as follows:
1. A white fixation point will appear at the center
2. Keep your eyes on the fixation point
3. A red target will appear - move your eyes to it
4. Another red target will appear - move your eyes to it
5. The fixation point will reappear at the center

Please keep your head still and only move your eyes.

Press SPACE to begin, or ESC to quit.""",
            height=0.8,
            wrapWidth=30,
            color='white'
        )
        
        instructions.draw()
        self.win.flip()
        
        keys = event.waitKeys(keyList=['space', 'escape'])
        if 'escape' in keys:
            self.cleanup()
            core.quit()  # Exit program
    
    def run_trial(self, trial):
        """
        Run a single trial.
        
        Args:
            trial: Dictionary containing trial parameters
        """
        # Show fixation
        self.fixation.pos = [trial['start_x'], trial['start_y']]
        self.fixation.draw()
        self.win.flip()
        core.wait(0.5 + np.random.rand() * 0.5)  # Random fixation duration 0.5-1s
        
        # Show first target (diagonal)
        self.target.pos = [trial['target1_x'], trial['target1_y']]
        self.target.draw()
        self.win.flip()
        core.wait(0.5)  # Target visible for 500ms
        
        # Show second target (horizontal or vertical from first)
        self.target.pos = [trial['target2_x'], trial['target2_y']]
        self.target.draw()
        self.win.flip()
        core.wait(0.5)  # Target visible for 500ms
        
        # Blank screen
        self.win.flip()
        core.wait(0.3)  # Inter-trial interval
        
        # Check for escape key
        keys = event.getKeys(['escape'])
        if 'escape' in keys:
            return False
        
        return True
    
    def run(self):
        """Run the full experiment."""
        self.show_instructions()
        
        # Run all trials
        for trial_num, trial in enumerate(self.trials):
            # Add trial to experiment handler
            self.exp_handler.addData('trial_num', trial_num)
            for key, value in trial.items():
                self.exp_handler.addData(key, value)
            
            # Run the trial
            continue_exp = self.run_trial(trial)
            
            # Next entry in data file
            self.exp_handler.nextEntry()
            
            if not continue_exp:
                break
            
            # Show progress every 10 trials
            if (trial_num + 1) % 10 == 0:
                progress_text = visual.TextStim(
                    self.win,
                    text=f"Trial {trial_num + 1} of {len(self.trials)}\n\nPress SPACE to continue",
                    height=0.8,
                    color='white'
                )
                progress_text.draw()
                self.win.flip()
                event.waitKeys(keyList=['space'])
        
        # Show end message
        end_text = visual.TextStim(
            self.win,
            text="Experiment complete!\n\nThank you for participating.\n\nPress SPACE to exit.",
            height=0.8,
            color='white'
        )
        end_text.draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])
        
        self.cleanup()
        core.quit()  # Exit program
    
    def cleanup(self):
        """Clean up resources."""
        self.win.close()


def main():
    """Main function to run the experiment."""
    # Get participant information
    dlg = gui.Dlg(title="Double Saccade Experiment")
    dlg.addField('Participant ID:')
    dlg.addField('Distance (deg):', 10)
    dlg.addField('Repetitions:', 5)
    dlg.show()
    
    if dlg.OK:
        participant_id = dlg.data[0].strip()
        
        # Validate participant ID
        if not participant_id:
            print("Error: Participant ID cannot be empty")
            return
        
        # Validate and convert numeric inputs
        try:
            distance = float(dlg.data[1])
            repetitions = int(dlg.data[2])
            
            if distance <= 0:
                print("Error: Distance must be positive")
                return
            if repetitions <= 0:
                print("Error: Repetitions must be positive")
                return
                
        except ValueError as e:
            print(f"Error: Invalid numeric input - {e}")
            return
        
        # Create and run experiment
        exp = DoubleSaccadeExperiment(
            participant_id=participant_id,
            distance=distance,
            repetitions=repetitions
        )
        exp.run()
    else:
        print("Experiment cancelled by user")


if __name__ == '__main__':
    main()

