# Gaze Writing Program
Works best in a linux environment. On windows just use WSL unless you hate yourself.

Setup:

```
sudo apt install git python3 python3-pip cmake
pip3 install numpy pandas openpyxl opencv_python dlib

git clone https://github.com/kunalchandan/EyeLance.git
cd EyeLance
git clone https://github.com/antoinelame/GazeTracking.git

python3 gaze_wrapper.py --input-video input_video.mp4 --output-sheet output-sheet.xlsx

```