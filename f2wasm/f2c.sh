#!/bin/sh

# Check if any arguments are provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 [options] file1.f [file2.f ...]"
    exit 1
fi

# Initialize variables to store options and files
options=""
files=""

# Parse command-line arguments
for arg in "$@"; do
    # Check if the argument starts with a hyphen (option)
    case "$arg" in
        -*) options="$options $arg" ;;
        *) files="$files $arg" ;;
    esac
done

# Check if any Fortran files were provided
if [ -z "$files" ]; then
    f2c $options</dev/null
#    echo "Error: No Fortran files specified."
#    exit 1
fi

# Loop through the files and invoke f2c for each
for file in $files; do
    # Verify the file ends with .f or .F
    case "$file" in
        *.f | *.F)
            echo "Processing $file with options: $options"
            # Invoke f2c with the collected options and the current file
            f2c $options "$file"
            if [ $? -ne 0 ]; then
                echo "Error: f2c failed for $file"
                exit 1
            fi
            ;;
        *)
            echo "Warning: Skipping $file (does not end in .f or .F)"
            ;;
    esac
done

exit 0