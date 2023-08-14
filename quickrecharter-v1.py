import os
import shutil
import json
import copy

# === Displays ===
def display_main_menu():
    print("\nWelcome to Note Switcher!")
    print("What would you like to do?")
    print("1 - Edit specific chart")
    print("2 - Edit all charts")
    print("3 - Exit (Ctrl + C to force exit at any time! Changes may or may not save however...)")

# Menu for editing charts
def display_chart_menu(charts):
    print("\nWhat chart would you like to edit?")

    for i, chart in enumerate(charts):
        print(f"{i + 1} - {chart['name']}")
    
    print(f"{i + 2} - Go Back")

# Menu for when user has to choose which input_type to change
def display_input_type_editor(chart_name):
    print(f"\nChart: {chart_name}")
    print("What input_type would you like to change? (0 - 3)")
    print("Or, type y/n to either accept/reject changes!")

# Menu for when user has to choose which input_type to change for all charts
def display_input_type_editor_all_charts():
    print(f"\nYou're now editing ALL charts:")
    print("What input_type would you like to change? (0 - 3)")
    print("Or, type y/n to either accept/reject changes!")

# Success message for editing a chart
def display_chart_modified_successfully(chart_name, num_input_types):
    version_text = f"{num_input_types} note version"
    print(f"\nChart '{chart_name}' has been modified successfully!\nChart is a {version_text} of the original chart!")

# Message for when no changes have been made for a chart
def display_no_changes_made(chart_name):
    print(f"Chart '{chart_name}' has not been changed!")

# Invalid option message
def display_invalid_choice_message():
    print("Invalid choice. Please try again.")

# Message for when Ctrl + C is pressed
def display_program_interrupted():
    print("\nInput interrupted by Ctrl + C! Force exiting...")
    print("Changes may or may not have been saved!")
    exit()

# === Prompts ===
# Ask user for level folder path, then validate it, clone it, and validate cloned level folder
def prompt_for_folder_path():
    try:
        folder_path = input("Welcome to Note Switcher!\nEnter the folder path to your level: ")
    except KeyboardInterrupt:
        display_program_interrupted()

    # Validate the folder path
    if not validate_folder_path(folder_path):
        print("Invalid folder path. Please provide a valid folder path containing a 'config' folder and 'notes.cfg' file.")
        exit()

    print("Folder path validated!")

    # Check for duplicate folder names
    i = 1
    while True:
        if i == 1:
            # Clone the entire folder
            destination_folder = folder_path + ' - Copy'  # Add a suffix to the folder name for the copied folder
        else:
            destination_folder = folder_path + f' - Copy({i})'

        try:
            shutil.copytree(folder_path, destination_folder)
            break
        except FileExistsError:
            i += 1

    # Validate the cloned folder path
    if not validate_folder_path(destination_folder):
        print("Something went wrong with cloning level folder, please try again!")
        exit()

    print("Original level folder was cloned successfully!")

    return grab_json_from_cfg(destination_folder)

def prompt_user_input():
    try:
        choice = input("Enter your choice: ")
    except KeyboardInterrupt:
        display_program_interrupted()
    
    return choice

# Prompts user for which input_types to edit
def prompt_input_type_change(chart_name):
    # Prompt user for which input_type to change
    display_input_type_editor(chart_name)
    old_input_type = prompt_user_input()

    if old_input_type.isnumeric() and 0 <= int(old_input_type) <= 3: # Chose an input_type to change
        new_input_type = input("What would you like to change this to? (0 - 3): ")
        print(f"\ninput_type '{old_input_type}' will be changed to '{new_input_type}'")
        return int(old_input_type), int(new_input_type)
    elif old_input_type.lower() == 'y': # Accept changes
        return True
    elif old_input_type.lower() == 'n': # Reject changes
        return False
    else:
        display_invalid_choice_message()

# Prompts user for which input_types to edit for all charts
def prompt_input_type_change_all_charts():
    # Prompt user for which input_type to change
    display_input_type_editor_all_charts()
    old_input_type = prompt_user_input()

    if old_input_type.isnumeric() and 0 <= int(old_input_type) <= 3: # Chose an input_type to change
        new_input_type = input("What would you like to change this to? (0 - 3): ")
        print(f"\ninput_type '{old_input_type}' will be changed to '{new_input_type}'")
        return int(old_input_type), int(new_input_type)
    elif old_input_type.lower() == 'y': # Accept changes
        return True
    elif old_input_type.lower() == 'n': # Reject changes
        return False
    else:
        display_invalid_choice_message()

# Prompts user for what to append to end of cloned chart
def prompt_cloned_chart_name_change():
    chart_append_text = input("What would you like to append to this chart variant's name: ")
    return chart_append_text

# === Functions ===
def validate_folder_path(folder_path):
    # Checks if the folder path contains a 'config' folder and 'notes.cfg' file
    config_folder = os.path.join(folder_path, 'config')
    notes_cfg_file = os.path.join(config_folder, 'notes.cfg')

    return os.path.isdir(config_folder) and os.path.isfile(notes_cfg_file)

# Grab JSON from the 'notes.cfg' file
def grab_json_from_cfg(destination_folder):
    # Open the 'config' folder
    config_folder = os.path.join(destination_folder, "config")

    # Read the 'notes.cfg' file
    notes_cfg_file = os.path.join(config_folder, "notes.cfg")
    with open(notes_cfg_file, 'r') as cfg_file:
        cfg_contents = cfg_file.read()

    # Extract the JSON data from the 'data' variable
    start_index = cfg_contents.find('{')
    end_index = cfg_contents.rfind('}') + 1
    json_data = cfg_contents[start_index:end_index]
    return destination_folder, notes_cfg_file, json.loads(json_data)


def apply_input_type_change(cloned_chart, old_input_type, new_input_type):
    # For loop to switch each input_type to another one in 'notes'
    for note in cloned_chart['notes']:
        if note['input_type'] == old_input_type:
            note['input_type'] = new_input_type

# === Menus ===
def edit_specific_chart_menu(existing_charts, no_changes):
    # Count the number of existing charts
    existing_chart_count = len(existing_charts)

    # Determine the starting rating based on the first chart's rating
    starting_rating = existing_charts[0]['rating'] + existing_chart_count

    # Specific chart edit menu
    while True:
        display_chart_menu(existing_charts)
        chart_choice = prompt_user_input()

        # Chosen chart choice
        if chart_choice.isnumeric() and 1 <= int(chart_choice) <= existing_chart_count:
            # Grab chart index, then grab chosen chart
            chart_index = int(chart_choice) - 1
            chart = existing_charts[chart_index]

            input_changes = [] # Define list of input changes

            # input_type editor menu
            while True:
                input_choice = prompt_input_type_change(chart['name']) # Prompt user for which input_type to change to what

                # Accept or reject changes choice
                if isinstance(input_choice, bool):
                    break
                
                if input_choice is not None:
                    input_changes.append(input_choice) # Add change to list

            # If changes were accepted, do this
            if input_choice == True:
                # Clone entire chart object, this is an independant object, not a reference to original object
                cloned_chart = copy.deepcopy(chart)

                # Switch out inputs
                for old_input_type, new_input_type in input_changes:
                    apply_input_type_change(cloned_chart, old_input_type, new_input_type)

                # Checks for all unique input_types used in chart
                input_types_used = set(note['input_type'] for note in cloned_chart['notes'])
                num_input_types = len(input_types_used)

                # Ask user what to append to the end of the cloned chart name
                cloned_chart['name'] += prompt_cloned_chart_name_change()

                # Make sure the cloned chart is ordered correctly
                cloned_chart['rating'] = starting_rating + chart_index

                # Append cloned chart to the end of existing charts list
                existing_charts.append(cloned_chart)
                existing_chart_count = len(existing_charts) # Update number of existing charts

                # Display new chart name
                display_chart_modified_successfully(cloned_chart['name'], num_input_types)
                no_changes = False # Changes have been made so now exit process has to be different
            
            # If changes were rejected, do this
            else:
                display_no_changes_made(chart['name'])
        
        # Exit choice
        elif chart_choice.isnumeric() and existing_chart_count < int(chart_choice) < existing_chart_count + 2:
            break
        
        # Invalid choice
        else:
            display_invalid_choice_message()
    
    return no_changes

def edit_all_charts_menu(existing_charts, no_changes):
    # Count the number of existing charts
    existing_chart_count = len(existing_charts)

    # Determine the starting rating based on the first chart's rating
    starting_rating = existing_charts[0]['rating'] + existing_chart_count

    # Specific chart edit menu
    while True:
        input_changes = [] # Define list of input changes
        new_charts = [] # List to hold newly cloned charts

        # input_type editor menu
        while True:
            input_choice = prompt_input_type_change_all_charts() # Prompt user for which input_type to change to what

            # Accept or reject changes choice
            if isinstance(input_choice, bool):
                break
            
            if input_choice is not None:
                input_changes.append(input_choice) # Add change to list

        # If changes were accepted, do this
        if input_choice == True:
            for chart_index, chart in enumerate(existing_charts):
                # Clone entire chart object, this is an independant object, not a reference to original object
                cloned_chart = copy.deepcopy(chart)

                # Switch out inputs
                for old_input_type, new_input_type in input_changes:
                    apply_input_type_change(cloned_chart, old_input_type, new_input_type)

                # Checks for all unique input_types used in chart
                input_types_used = set(note['input_type'] for note in cloned_chart['notes'])
                num_input_types = len(input_types_used)

                # Ask user what to append to the end of the cloned chart name
                cloned_chart['name'] += f' - {num_input_types} Note Version'

                # Make sure the cloned chart is ordered correctly
                cloned_chart['rating'] = starting_rating + chart_index

                # Append cloned chart to the new_charts list, not existing_charts
                new_charts.append(cloned_chart)

                # Display new chart name
                display_chart_modified_successfully(cloned_chart['name'], num_input_types)
                no_changes = False # Changes have been made so now exit process has to be different

            # After the loop is done, append the new charts to the existing_charts list
            existing_charts.extend(new_charts)

            print("All changes were made successfully!")
            break
        
        # If changes were rejected, do this
        else:
            display_no_changes_made(chart['name'])
            break

    return no_changes


def main_menu(existing_charts, no_changes):
    # Main menu
    while True:
        display_main_menu()
        choice = prompt_user_input()

        # Edit specific chart choice
        if choice == '1':
            no_changes = edit_specific_chart_menu(existing_charts, no_changes)

        # Edit all charts choice
        elif choice == '2':
            no_changes = edit_all_charts_menu(existing_charts, no_changes)

        # Exit choice
        elif choice == '3':
            print("\nExiting Note Switcher...")
            break

        # Invalid choice
        else:
            display_invalid_choice_message()
    
    return no_changes

# === Beginning of Program ===
def start_program():
    # Prompt the user for a folder path
    destination_folder, notes_cfg_file, config_data = prompt_for_folder_path() # Returns parsed JSON data and 'notes.cfg' file path

    # Get the existing charts
    existing_charts = config_data['charts']
    no_changes = True # Only here if user does absolutely nothing and exits

    # Generate main menu
    no_changes = main_menu(existing_charts, no_changes)

    end_program(destination_folder, notes_cfg_file, config_data, no_changes)

def end_program(destination_folder, notes_cfg_file, config_data, no_changes):
    # Checks if user exited without making changes
    if no_changes is True:
        # Remove copied folder since it has no real changes
        shutil.rmtree(destination_folder)
        print("No changes were made.")
        exit()

    # Convert the updated configuration data back to JSON
    updated_json_data = json.dumps(config_data, indent=4)
    finalized_cfg_file = '[main]\ndata = ' + updated_json_data

    # Update the 'notes.cfg' file with the modified JSON data
    with open(notes_cfg_file, 'w') as cfg_file:
        cfg_file.write(finalized_cfg_file)

    print("Folder copied and notes.cfg modified successfully!")

start_program()