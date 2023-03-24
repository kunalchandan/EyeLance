# Gaze Writing Program
Works best in a linux environment. On windows just use WSL unless you hate yourself.

Setup:

```
sudo apt update
sudo apt upgrade

sudo apt install git cmake
sudo apt install ffmpeg libsm6 libxext6
sudo apt install python3 
sudo apt install python3-pip
pip3 install attrdict3 Gooey
pip3 install numpy pandas openpyxl opencv_python dlib

git clone https://github.com/kunalchandan/EyeLance.git
cd EyeLance
git clone https://github.com/antoinelame/GazeTracking.git

python3 gaze_wrapper.py --input-video input_video.mp4 --output-sheet output-sheet.xlsx

```

## Usage

### Launcher
![image](docs/launcher.png)

### Selecting a file
![image](docs/open_file.png)

### Begining marking video
This example has too few frames to fill the entire dataset so a warning is shown.

![image](docs/too_few_frames.png)

### Coding 
![image](docs/coding_data.png)

### Completion Screen
Can restart coding screen

Can also edit selection and code another video and output another excel sheet or overwrite the same one.
![image](docs/completion.png)

### Resulting output
![image](docs/output_sheet.png)

