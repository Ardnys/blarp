# Blarp

Blarp (blur and sharpen) is a Python script for applying Turing Pattern to images and videos. 

<p align="center">
  <img src="https://github.com/Ardnys/blarp/blob/master/images/bad_apple.png" width="45%"/>
  <img src="https://github.com/Ardnys/blarp/blob/master/images/bad_apple_blarped.png" width="45%"/>
</p>
<p align="center">
  <i>Original (left) vs. Blarped (right)</i>
</p>

## Context / Inspiration
I saw [What Happens if You Blur and Sharpen an Image 1000 Times?](https://youtu.be/7oCtDGOSgG8?si=RGmcMpYZpPLZ5OB8) by Patrick Gillespie and I was inspired to try it myself.
I had to apply this idea to [Bad Apple!!](https://youtu.be/FtutLA63Cp8?si=XOHYw8zyb1ccus8g) to fulfill a missing piece of "Bad Apple!! but" internet gag.

Apparently Patrick already wrote [a script](https://github.com/patorjk/video-to-turing-pattern) for his video. One improvement of my script is that it uses GLSL shaders to blur and sharpen images,
so it's **A LOT** faster than doing convolutions with CPU. My computer (mobile RTX GPU) can blarp the bad apple video in a few minutes, rather than half an hour (I first tried it on CPU but it was too slow).

## Getting Started

To get started with Blarp, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Ardnys/blarp.git
    cd blarp
    ```

2.  **Install `uv` (if you haven't already):**
    `uv` is a fast Python package installer and resolver. You can find installation instructions [here](https://astral.sh/uv/install/).

3.  **Install dependencies:**
    ```bash
    uv sync
    ```
    This project has been tested with Python 3.12. It should work (fingers crossed) with >3.12 too, give it a try.

4.  **Install `ffmpeg`:**
    `ffmpeg` is required for video to video blarping. Make sure it's installed and available in your system's PATH. You can download it from the official website [here](https://ffmpeg.org/download.html).

## Usage Examples

### Command Line Arguments

```
usage: main.py [-h] -i INPUT_MEDIA -o OUTPUT_MEDIA [-n NUM_BLARP] [--fps FPS] [--max-frames MAX_FRAMES]

Blarp (blur and sharpen) videos and images a lot of times for interesting effects

options:
  -h, --help               show this help message and exit
  -i INPUT_MEDIA,          --input-media INPUT_MEDIA
  -o OUTPUT_MEDIA,         --output-media OUTPUT_MEDIA
  -n NUM_BLARP,            --num-blarp NUM_BLARP
  --fps FPS
  --max-frames MAX_FRAMES  End blarping after this much frames (video to video only)
```
**⚠️ SEIZURE WARNING ⚠️**

Blarped video is NOT easy on the eyes. Be careful.

### Image to Image

To blarp an image and save the result:

```bash
uv run main.py -i input.jpg -o output_blarped.jpg
```

For more blarping, give a bigger number with `-n` flag (default 750).

### Image to Video

To create a blarped video from an image:

```bash
uv run main.py -i input.jpg -o output_video.mp4 --fps 120
```
<p align="left">
  <img src="https://github.com/Ardnys/blarp/blob/master/images/HDpfp_blarped.gif" width="45%"/>
</p>
<p align="left">
  <i>Blarping of an image</i>
</p>

### Video to Video

To blarp a video 1000 times:

```bash
uv run main.py -i input_video.mp4 -o output_blarped_video.mp4 -n 1000 --fps 30
```


## Issues & Contributions

Issues and contributions are welcome! Feel free to open an issue or submit a pull request.


