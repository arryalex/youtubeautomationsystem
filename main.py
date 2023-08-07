import random
import os
import schedule
import time
from datetime import datetime
from Upload import upload
from Update import update_view_count_and_thumbnail


combinations = {
    "a": ["koushalmonga", "RajGrover005", "ChetanMongaVlogs",],
    "b": ["gulshankalra07", "varunbundela",'unknownboyvarun','amishaforyou' ],
    "c": ["TheVishalbhatt",'Mukesh_jaiswal', "sonu_indori",'bobbyprankster','payalpanchalofficial'],
    "d": ["realfoolsshorts63", "ShortsBreak_Official","Dushyant_kukreja", "Priyal_Kukreja"]
          
}

print("Your Program is running ;) ...")

current_index = 0
def Get_key_item():
    key = read_key_from_file()
    global current_index
    if key in combinations:
        key_list = combinations[key]
        if len(key_list) == 0:
            print(f"No items in the list for key '{key}'.")
            return
        item = key_list[current_index]
        print(f"{key} list item at {time.strftime('%H:%M:%S')}: {item}")
        current_index = (current_index + 1) % len(key_list)
        return item

def read_key_from_file():
    try:
        with open('Today.txt', 'r') as file:
            key = file.read().strip()
            print("The key stored in the file is:", key)
            return key
    except FileNotFoundError:
        print("File not found. Please provide a valid file path.")
    except Exception as e:
        print("An error occurred:", str(e))

def shuffle_combinations():
    temp_combinations = list(combinations.keys())
    random.shuffle(temp_combinations)
    return temp_combinations

def store_combinations(today_key:str=None, future_keys:str=None):
    with open('Today.txt', 'w') as file:
        if today_key is not None : 
            file.write(today_key)
    with open('future.txt', 'w') as file:
        if future_keys is not None:
            for key in future_keys:
                file.write(key + '\n')

def remove_data_store_files():
    files_to_remove = ['Today.txt', 'future.txt', 'Expired.txt']
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Removed {file_name}")
        else:
            print(f"{file_name} not found. Skipping.")

def move_keys_between_files_on_first_run():
    global moving_in_progress
    if moving_in_progress:
        return
    moving_in_progress = True
    with open('Today.txt', 'r') as file:
        today_key = file.readline().strip()
    with open('future.txt', 'r') as file:
        future_keys = [line.strip() for line in file]
    if not future_keys:
        print(f"{datetime.now()}: No keys in Future.txt. Stopping the key moving process.")
        moving_in_progress = False
        return
    new_today_key = future_keys.pop(0)
    with open('Today.txt', 'w') as file:
        file.write(new_today_key)
    with open('future.txt', 'w') as file:
        for key in future_keys:
            file.write(key + '\n')
    print(f"{datetime.now()}: Moved key: {new_today_key} to Today.txt. Key removed from future.txt.")
    moving_in_progress = False

def move_keys_between_files():
    global moving_in_progress
    if moving_in_progress:
        return
    moving_in_progress = True
    with open('Today.txt') as file:
        today_key = file.readline().strip()
    with open('future.txt') as file:
        future_keys = [line.strip() for line in file]
    if not future_keys:
        print(f"{datetime.now()}: No keys in Future.txt. Stopping the key moving process.")
        return
    expired_key = today_key
    today_key = future_keys[0]
    future_keys = future_keys[1:]
    with open('Expired.txt', 'a') as file:
        file.write(expired_key + '\n')
    store_combinations(today_key, future_keys)
    print(f"{datetime.now()}: Moved key: {expired_key}")
    moving_in_progress = False


def initial_setup():
    remove_data_store_files()
    keys = shuffle_combinations()
    future_keys = keys
    store_combinations(future_keys=future_keys)
    print(f"{datetime.now()}: Initial setup completed. Keys are stored.")


def Upload_Video():
    Get_key = Get_key_item()
    upload(file_name=Get_key)

def run_functions():
    current_hour = datetime.now().hour
    if 1 <= current_hour < 19:
        video_Id = Upload_Video()
        time.sleep(5 * 60)
        update_view_count_and_thumbnail(video_Id)

def main():
    global initial_setup_completed
    global moving_in_progress
    initial_setup_completed = False
    moving_in_progress = False
    initial_setup()
    move_keys_between_files_on_first_run()
    schedule.every(4).days.at("19:00").do(initial_setup)
    schedule.every(1).day.at("19:00").do(move_keys_between_files)
    schedule.every().hour.at(":30").do(run_functions)
    current_hour = datetime.now().hour
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
