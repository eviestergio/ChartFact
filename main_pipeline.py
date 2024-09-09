import os
import subprocess

def create_pipeline_folders(base_folder, num_entries):
    main_folder = f'{base_folder}_{num_entries}'
    subfolders = {
        '1': f'1_extracted_data_{num_entries}',
        '2': f'2_preprocessed_data_{num_entries}',
        '3': f'3_translated_data_{num_entries}',
        '4': f'3_translated_data_{num_entries}', # Step 4 (CSV formatting) uses the same folder as step 3 (CSV generation)
        '5': f'4_prompted_data_{num_entries}',  
        '6': f'5_final_dataset_{num_entries}'
    }

    for subfolder in subfolders.values():
        os.makedirs(os.path.join(main_folder, subfolder), exist_ok=True)
    
    return main_folder, subfolders

def run_scripts(script_path, args):
    if script_path.endswith('.ipynb'):
        # Set environment variables with full paths
        main_script_dir = os.path.dirname(os.path.abspath(__file__))
        src_full_path = os.path.abspath(os.path.join(main_script_dir, args[0]))
        dst_full_path = os.path.abspath(os.path.join(main_script_dir, args[1]))

        os.environ['SRC_PATH'] = src_full_path
        os.environ['DST_PATH'] = dst_full_path

        command = [
            'jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--inplace', 
            '--ExecutePreprocessor.timeout=600', script_path
        ]
    else:
        command = ['python', script_path] + args

    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f'Error running {script_path}: {result.stderr}')
    return 

def is_folder_empty(folder_path):
    """Check if a folder is empty."""
    return len(os.listdir(folder_path)) == 0

def main():
    #user inputs
    base_folder = input("Enter the base folder name (e.g., 'seed_datasets'): ")
    num_entries = input("Enter the number of entries (e.g., '100K' or '100_000'): ")
    default_source_folder = '~/Desktop/ChartFact/QA_datasets' # default source folder path 

    # ask user if they want to use default source folder path
    use_default = input(f"Do you want to use the default source folder path ({default_source_folder})? (yes/no): ").strip().lower()

    if use_default in ['yes', 'y']:
        source_folder = default_source_folder
    else:
        source_folder = input("Enter the source folder path: ")

    # expand user path '~' to full path
    source_folder = os.path.expanduser(source_folder)

    # create folders
    main_folder, subfolders = create_pipeline_folders(base_folder, num_entries)

    #paths to scripts
    extraction_script = 'data_extraction/random_extraction.py'
    preprocessing_script = 'data_preprocessing/file-data_standardisation.py'
    translation_script = 'data_translation/deplot.py' #default translation model: DePlot, not Chart-to-Table
    formatting_script = 'data_translation/deplot_CSV_format.ipynb'
    prompting_script = 'data_prompting/main.py'
    final_script = 'final_dataset_creation/combine_datasets.py'

    # define steps
    steps = {
        '1': ('Data Extraction', extraction_script, [source_folder, os.path.join(main_folder, subfolders['1'])]),
        '2': ('Data Preprocessing', preprocessing_script, [os.path.join(main_folder, subfolders['1']), os.path.join(main_folder, subfolders['2'])]),
        '3': ('Data Translation', translation_script, [os.path.join(main_folder, subfolders['2']), os.path.join(main_folder, subfolders['3'])]),
        '4': ('Data Formatting', formatting_script, [os.path.join(main_folder, subfolders['3']), os.path.join(main_folder, subfolders['4'])]),
        '5': ('Data Prompting', prompting_script, [os.path.join(main_folder, subfolders['4']), os.path.join(main_folder, subfolders['5'])]),
        '6': ('Final Dataset Creation', final_script, [os.path.join(main_folder, subfolders['5']), os.path.join(main_folder, subfolders['6'])])
    }

    # explain steps
    print("Pipeline steps:")
    print("1: Data Extraction")
    print("2: Data Preprocessing")
    print("3: Data Translation")
    print("4: Data Formatting")
    print("5: Data Prompting")
    print("6: Final Dataset Creation")

    current_step = 1
    while current_step <= 6:
        step_name, script, args = steps[str(current_step)]
        next_step = input(f"Do you want to run step {current_step}: {step_name}? (yes/no): ").strip().lower()
        
        if next_step in ['yes', 'y']:
            # script, args = steps[str(current_step)]
            run_scripts(script, args)
        else:
            input(f"Please complete step {current_step} manually and press Enter to continue...")
        
        if current_step > 1:
            previous_folder = os.path.join(main_folder, subfolders[str(current_step - 1)])
            if is_folder_empty(previous_folder):
                print(f"Step {current_step} requires step {current_step - 1} to be completed. Please complete the previous step manually and try again.")
                continue
        
        current_step += 1

    print('Pipeline completed successfully.')

if __name__=='__main__':
    main()