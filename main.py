import argparse
from pathlib import Path
from core.processor import (
    ImageToImageProcessor,
    ImageToVideoProcessor,
    VideoToVideoProcessor,
)
from core.blarp import ModernGL, Blarp


def choose_processor(args, blarp):
    in_path = args.input_media
    out_path = args.output_media

    # Determine mode based on extensions
    img_exts = {".jpg", ".jpeg", ".png", ".bmp"}
    vid_exts = {".mp4", ".mov", ".avi", ".mkv"}

    in_ext, out_ext = in_path.suffix.lower(), out_path.suffix.lower()

    if in_ext in img_exts and out_ext in img_exts:
        return ImageToImageProcessor(blarp, args)
    elif in_ext in img_exts and out_ext in vid_exts:
        return ImageToVideoProcessor(blarp, args)
    elif in_ext in vid_exts and out_ext in vid_exts:
        return VideoToVideoProcessor(blarp, args)
    else:
        raise ValueError(
            f"Unsupported input/output combination: {in_ext} → {out_ext}")


def main():
    parser = argparse.ArgumentParser(
        description="Blarp (blur and sharpen) videos and images a lot of times for interesting effects"
    )
    parser.add_argument("-i", "--input-media", type=Path, required=True)
    parser.add_argument("-o", "--output-media", type=Path, required=True)
    parser.add_argument("-n", "--num-blarp", type=int, default=750)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--max-frames", type=int,
                        help="End blarping after this much frames")
    args = parser.parse_args()

    mgl = ModernGL()
    blarp = Blarp(mgl)
    processor = choose_processor(args, blarp)
    processor.run()
    mgl.release_all()


if __name__ == "__main__":
    main()
