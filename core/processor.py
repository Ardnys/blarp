from abc import ABC, abstractmethod
import cv2
import subprocess
from pathlib import Path
from PIL import Image
from tqdm import tqdm
from core.blarp import Blarp


class Processor(ABC):
    """Base processor interface for different input/output modes."""

    def __init__(self, blarp: Blarp, args):
        self.blarp = blarp
        self.args = args

    @abstractmethod
    def run(self):
        pass


class ImageToImageProcessor(Processor):
    def run(self):
        img = Image.open(self.args.input_media).convert("RGB")
        result = self.blarp(img, self.args.num_blarp)
        Image.fromarray(result).save(self.args.output_media)
        print(f"✅ Saved blarped image to {self.args.output_media}")


class ImageToVideoProcessor(Processor):
    def run(self):
        img = Image.open(self.args.input_media).convert("RGB")
        width, height = img.size
        out = cv2.VideoWriter(
            str(self.args.output_media),
            cv2.VideoWriter_fourcc(*"mp4v"),
            self.args.fps,
            (width, height),
        )

        # cv2.VideoWriter is not thread-safe, so frames are written
        # synchronously, in the order they are generated.
        for i in tqdm(range(self.args.num_blarp), desc="Generating frames"):
            result = self.blarp(img, i + 1)
            frame = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
            out.write(frame)

        out.release()
        print(f"✅ Saved blarping video to {self.args.output_media}")


class VideoToVideoProcessor(Processor):
    def __init__(self, blarp, args):
        super().__init__(blarp, args)

        # we need an extra file to write video
        # because ffmpeg doesn't accept the same file for input and output
        self.tempfile = Path(args.output_media).with_suffix(".tmp.mp4")

    def run(self):
        vid = cv2.VideoCapture(str(self.args.input_media))

        total = self.args.max_frames if self.args.max_frames else int(
            vid.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(
            str(self.tempfile),
            cv2.VideoWriter_fourcc(*"mp4v"),
            self.args.fps,
            (width, height),
        )

        try:
            # cv2.VideoWriter is not thread-safe, so frames are written
            # synchronously, in the order they are read.
            for i in tqdm(range(total), desc="Blarping video"):
                ok, frame = vid.read()
                if not ok:
                    break
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                result = self.blarp(img, self.args.num_blarp)
                frame = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
                out.write(frame)
        finally:
            vid.release()
            out.release()

        if self.tempfile.exists():
            self.merge_audio_video()
            # remove when it's done
            self.tempfile.unlink()

        print(f"✅ Saved blarped video to {self.args.output_media}")

    def merge_audio_video(self):
        cmd = [
            "ffmpeg",
            "-loglevel", "+error",
            "-y",  # overwrite existing file
            "-i", str(self.tempfile),
            "-i", str(self.args.input_media),
            "-c:v", "copy",
            "-map", "0:v:0",  # first input's video stream
            "-map", "1:a:0",  # second input's audio stream
            "-shortest",
            str(self.args.output_media)
        ]

        subprocess.run(cmd, check=True)
