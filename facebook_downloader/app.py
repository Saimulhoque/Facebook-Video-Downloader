# import yt_dlp


# def download_facebook_video(fb_url, output_filename="facebook_video.mp4"):
#     ydl_opts = {
#         'format': 'best',  # Fetch the best quality available
#         'outtmpl': output_filename,  # Set output filename
#     }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             ydl.download([fb_url])
#         print(f"Video downloaded successfully as {output_filename}.")
#     except Exception as e:
#         print(f"Error downloading video: {e}")


# # Facebook video URL
# fb_url = 'https://www.facebook.com/shezenfitness/videos/8172358746226684'

# # Download the video
# download_facebook_video(fb_url, "shezenfitness_video.mp4")

from flask import Flask, render_template, request, jsonify
import os
import yt_dlp
import threading

app = Flask(__name__)

# Directory to save downloaded Facebook videos
DOWNLOAD_FOLDER = 'facebook_videos'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Global variable to track download progress
progress_data = {"progress": 0}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        fb_url = request.json.get('fb_url')
        if fb_url:
            try:
                progress_data["progress"] = 0  # Reset progress
                threading.Thread(target=download_facebook_video,
                                 args=(fb_url,)).start()
                return jsonify({"status": "success"}), 200
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
    return render_template('index.html')


@app.route('/progress_status')
def progress_status():
    return jsonify(progress_data)


def download_facebook_video(fb_url):
    global progress_data
    output_filename = os.path.join(DOWNLOAD_FOLDER, 'facebook_video.mp4')
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_filename,
        'progress_hooks': [progress_hook],  # Add progress hook for tracking
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([fb_url])
    except Exception as e:
        print(f"Error downloading video: {e}")
    progress_data["progress"] = 100  # Mark progress as 100% on completion


def progress_hook(d):
    global progress_data
    if d['status'] == 'downloading':
        # Get the percentage downloaded
        percentage = d.get('downloaded_bytes', 0) / \
            d.get('total_bytes', 1) * 100
        progress_data["progress"] = percentage
    elif d['status'] == 'finished':
        progress_data["progress"] = 100  # Ensure it's set to 100 when finished


# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True)
