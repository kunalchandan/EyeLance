import cv2

import pandas as pd
import numpy as np

import argparse
from gooey import Gooey, GooeyParser

import pathlib
from typing import Tuple



FONT_COLOUR = (255, 0, 0)
FONT_SCALE = 0.6
FONT = cv2.FONT_HERSHEY_DUPLEX

NUMBER_OF_TRIALS = 16
FRAMES_PER_TRIAL = 516


@Gooey(program_name='EyeLance')
def argument_parser() -> Tuple[pathlib.Path, pathlib.Path]:
    parser = GooeyParser(description=
                                     '''
Program for manual labeling of eye-tracking data.
Outputs an excel sheet with the corresponding data in the format of:
Frame # Trial 1 | Coding Trial 1 | Frame # Trial 2 | Coding Trial 2 | ...
--------------------------------------------------------------------------
...
''')
    parser.add_argument('--input-video',
                        dest='input_file',
                        type=str,
                        required=True,
                        help='name of input file',
                        widget='FileChooser',
                        )
    parser.add_argument('--output-sheet',
                        dest='output_file',
                        type=str,
                        required=True,
                        help='name of output file',
                        widget='FileChooser',
                        )
    args = parser.parse_args()

    video_file = args.input_file
    output_sheet = args.output_file

    return (video_file, output_sheet)



def annotate_frame(new_frame, direction: str, trial_number: int, trial_frame: int) -> np.ndarray:
    cv2.putText(new_frame, f"Detected direction: {direction}", (300, 260), FONT, FONT_SCALE, FONT_COLOUR, 2)
    cv2.putText(new_frame, f"Use detected 'W' key (Auto)", (300, 290), FONT, FONT_SCALE, FONT_COLOUR, 2)
    cv2.putText(new_frame, f"Coding Scheme: (Q=Black) (W=Auto)  (E=Flash)", (300, 330), FONT, FONT_SCALE, FONT_COLOUR, 2)
    cv2.putText(new_frame, f"Coding Scheme: (A=Left)  (S=Other) (D=Right) ", (300, 360), FONT, FONT_SCALE, FONT_COLOUR, 2)
    cv2.putText(new_frame, f"Trial Number {trial_number}", (60, 300), FONT, FONT_SCALE, FONT_COLOUR, 2)
    cv2.putText(new_frame, f"Trial Frame {trial_frame}", (60, 330), FONT, FONT_SCALE, FONT_COLOUR, 2)
    return new_frame


def skip_frames(video, total_frames, num_skipped_frames, winname):
    # UI to skip initial portion of video
    skipping = True
    while skipping:
        num_skipped_frames += 1
        still_reading, frame = video.read()
        cv2.putText(frame, f"Press M to begin annotation", (60, 250), FONT, FONT_SCALE*2, (0, 0, 255), 2)
        cv2.putText(frame, f"Skip frame with any key", (60, 200), FONT, FONT_SCALE, FONT_COLOUR, 2)

        if (total_frames - num_skipped_frames) < NUMBER_OF_TRIALS*FRAMES_PER_TRIAL:
            cv2.putText(frame, f"LIKELY TOO FEW FRAMES LEFT", (60, 300), FONT, FONT_SCALE*2, (0, 0, 255), 2)
            cv2.putText(frame, f"Need minimum of {NUMBER_OF_TRIALS*FRAMES_PER_TRIAL}", (60, 400), FONT, FONT_SCALE*2, (0, 0, 255), 2)
            cv2.putText(frame, f"Have ~ {total_frames - num_skipped_frames} left", (60, 480), FONT, FONT_SCALE*2, (0, 0, 255), 2)
        cv2.imshow(winname, frame)

        key_input = chr(cv2.waitKey(0)).lower()
        if cv2.getWindowProperty(winname, 0) < 0:
            print("QUITTING WITHOUT WRITING ANYTHING!!")
            exit()
        if key_input == "m":
            skipping = False



def process_video(video_file: pathlib.Path, output_sheet_path) -> pd.DataFrame:
    # Get Video
    video = cv2.VideoCapture(video_file)

    if not video.isOpened():
        print("Could not open: ", video_file)
        return
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_number = 0

    # Initialize Dataframe
    columns = np.array([[f'FrameNumber-Trial-{i:02}', f'Coding-Trial-{i:02}'] for i in range(1, NUMBER_OF_TRIALS+1)]).flatten()
    _ = np.empty((FRAMES_PER_TRIAL, NUMBER_OF_TRIALS*2), dtype=str)
    gaze_direction = pd.DataFrame(columns=columns)

    winname = "Video Frames"
    cv2.namedWindow(winname)
    cv2.moveWindow(winname, 40,30)

    num_skipped_frames = 0
    # IDK if this while loop is helping
    while cv2.getWindowProperty(winname, 0) >= 0:
        # UI to actually begin labelling
        for trial_number in range(1, NUMBER_OF_TRIALS+1):
            skip_frames(video, total_frames, num_skipped_frames, winname)
            for trial_frame in range(FRAMES_PER_TRIAL):
                still_reading, frame = video.read()
                if not still_reading:
                    return gaze_direction
                direction = 'Other'
                annotated_frame = annotate_frame(frame, direction, trial_number, trial_frame)
                cv2.imshow(winname, annotated_frame)
                frame_number += 1

                key_input = chr(cv2.waitKey(0)).lower()
                if cv2.getWindowProperty(winname, 0) < 0:
                    print("QUITTING WITHOUT WRITING ANYTHING!!")
                    exit()

                # User is slow write what the computer thinks
                if key_input == -1:
                    key_input = 'w'

                if key_input == 'a':
                    direction = 'Right'
                elif key_input == 's':
                    direction = 'Other'
                elif key_input == 'd':
                    direction = 'Left'
                elif key_input == 'q':
                    direction = 'Black'
                elif key_input == 'e':
                    direction = 'Flash'
                elif key_input == 'w': # Computer's best guess
                    direction = direction
                elif key_input == 'k': # Skip frame
                    continue

                gaze_direction.loc[trial_frame, f'FrameNumber-Trial-{trial_number:02}'] = frame_number
                gaze_direction.loc[trial_frame, f'Coding-Trial-{trial_number:02}'] = direction
                gaze_direction.to_csv(f"{output_sheet_path}-Intermediary.csv", index=False)
        return gaze_direction
    return gaze_direction


def main():
    video_file, output_sheet = argument_parser()
    gaze_data = process_video(video_file, output_sheet)

    print(gaze_data)
    gaze_data.to_excel(output_sheet, index=False)


if __name__ == "__main__":
    main()
