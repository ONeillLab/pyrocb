# Sylvio Dos Reis, 2026
# Runs python script for plotting the observed satellite fire perimeter and simulated fire perimeter by frame, passing in the specific run path, as well as the path of the analysis top level folder.

# The select command uses the PS3 variable for its prompt text
PS3="Enter the fire to analyse: "

# Using an array of files (*.conf) ensures filenames with spaces don't break the menu
select profile in "$PCB_OUTPUT_DIR/complete/"*; do
    # Check if the user entered a valid number
    if [[ -n "$profile" ]]; then
        echo "Analysing: $profile"
        
        python "$PCB_SCRIPTS_DIR/analysis/fire/perimetre.py" "$profile" "$PCB_OUT_DIR/analysis/"
        
        break # Exits the menu loop after a valid selection
    else
        echo "Invalid selection. Please try again."
    fi
done