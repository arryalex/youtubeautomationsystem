from pytube import YouTube

def download_video(link):
    try : 
        youtube_object = YouTube(link)
        youtube_object = youtube_object.streams.get_highest_resolution()
        try:
            download_folder = 'Downloaded Video/'
            file_name = 'Upload' + '.mp4'
            video_path = download_folder + file_name
            youtube_object.download(output_path=download_folder, filename=file_name)
            print("Download is completed successfully.")
            return video_path
        except Exception as e:
            print("An error has occurred:", str(e))
            return None
    except Exception as e:
        print("An error has occurred:", str(e))
        
# if __name__ == "__main__":
#     link = input("Enter the YouTube video URL: ")
#     video_path = download_video(link)
#     if video_path:
#         print("Video saved at:", video_path)
#     else:
#         print("Failed to download the video.")