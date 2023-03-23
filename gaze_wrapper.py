from GazeTracking.gaze_tracking import GazeTracking
import cv2
import pandas as pd
import argparse
import pathlib
from typing import List, Tuple


def argument_parser() -> Tuple[pathlib.Path, pathlib.Path]:
    parser = argparse.ArgumentParser(description='Process input and output file names')
    parser.add_argument('--input-video', dest='input_file', type=str, required=True, help='name of input file')
    parser.add_argument('--output-sheet', dest='output_file', type=str, required=True, help='name of output file')
    args = parser.parse_args()

    video_file = args.input_file
    output_sheet = args.output_file

    return [video_file, output_sheet]


def process_video(video_file: pathlib.Path) -> pd.DataFrame:
    video = cv2.VideoCapture(video_file)
    gaze = GazeTracking()
    font_colour = (255, 0, 0)
    font_scale = 1
    font = cv2.FONT_HERSHEY_DUPLEX


    frame_number = 0
    gaze_direction = pd.DataFrame(columns=['FrameNumber', 'Direction'])

    winname = "Video Frames"
    cv2.namedWindow(winname)
    cv2.moveWindow(winname, 40,30)

    while cv2.getWindowProperty(winname, 0) >= 0:
        still_reading, frame = video.read()
        if not still_reading:
            break
        gaze.refresh(frame)
        direction = 'Other'
        if gaze.is_right():
            direction = 'Right'
        elif gaze.is_left():
            direction = 'Left'
        elif gaze.is_center():
            direction = 'Other'
        else:
            direction = 'Other'

        new_frame = gaze.annotated_frame()
        cv2.putText(new_frame, f"Computer's Guess: {direction}", (60, 60), font, font_scale, font_colour, 2)
        cv2.putText(new_frame, f"Override with:\n(A=Left)\n(D=Right)\n(S=Other)", (60, 100), font, font_scale, font_colour, 2)
        cv2.putText(new_frame, f"Skip Frame with K key", (60, 200), font, font_scale, font_colour, 2)
        cv2.putText(new_frame, f"Use Computer Guess with Q key", (60, 250), font, font_scale, font_colour, 2)
        cv2.imshow(winname, new_frame)
        frame_number += 1

        key_input = chr(cv2.waitKey(0)).lower()
        if key_input == -1:
            key_input = 'q'
            
        if key_input == 'a':
            direction = 'Left'
        elif key_input == 's':
            direction = 'Other'
        elif key_input == 'd':
            direction = 'Right'
        elif key_input == 'q':
            direction = direction
        elif key_input == 'k':
            continue

        gaze_direction.loc[len(gaze_direction)] = (frame_number, direction)
    return gaze_direction


def main():
    video_file, output_sheet = argument_parser()
    gaze_data = process_video(video_file)

    print(gaze_data)
    gaze_data.to_excel(output_sheet, index=False)


if __name__ == "__main__":
    main()
