# The select command uses the PS3 variable for its prompt text
PS3="Enter the number of the config file you want to use: "

# Using an array of files (*.conf) ensures filenames with spaces don't break the menu
select profile in "$PCB_PROFILES_DIR"/*/; do
    # Check if the user entered a valid number
    if [[ -n "$profile" ]]; then
        echo "Loading: $profile"
        
        rsync -a $profile $PCB_PRE_DIR/profile
        
        break # Exits the menu loop after a valid selection
    else
        echo "Invalid selection. Please try again."
    fi
done