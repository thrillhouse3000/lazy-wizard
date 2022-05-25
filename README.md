# INTRODUCTION

The Lazy Wizard encounter generator uses the open5e API (https://api.open5e.com) to contsruct balanced encounters for Dungeons and Dragons 5e campaigns. Encounters can be built manually or generated randomly from the application.

This application is delpoyed at https://lazy-wizard.herokuapp.com/

# TECHNOLOGIES

- Python
- Flask
- Javascript
- HTML
- CSS

# REQUIREMENTS

Requirements can be found in the requirements.txt file.

# DEPLOYMENT

This application follows standard installation procedures.
Install the dependencies with:    

pip install -r requirements.txt

# FUNCTIONALITY

#### Encounter Builder
1. Create Your Party:
    - Add players to reflect your party's members
2. Calculate Encounter CRs:
    - Select your desired difficulty and monster amount
    - The appropriate CRs for the encounter will automatically be displayed in this section
3. Add Monsters or Generate An Encounter:
    - Monsters can be added here by name. Spelling and punctuation matters, but the input is case insensitive
    - Clicking the Generate Random Encounter will pull random monsters of the appropriate CRs from the API
4. Search by Type and CR:
    - Select a monster type or a valid CR (between 0 and 30) to generate a list of available monsters
    - Clicking on a monsters name in the search section will add it to the page
5. Save Encounter
    - A user must be logged in to save their encounter
    - The title of the encounter is required

### My Profile
The profile page will display a list of all of the user's saved encounters. Encounters can be deleted from thie view. Clicking on an encounter will load it in the encounter builder screen. The update button will save the encounter with the current data 


