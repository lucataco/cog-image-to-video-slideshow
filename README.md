# Image to Video Slideshow

A Replicate Cog model that creates beautiful MP4 video slideshows from a collection of images with customizable transitions, aspect ratios, and timing.

## Features

- 🖼️ **Multiple Image Support**: Process 2-50 images in a single slideshow
- 🎬 **Transition Effects**: Choose from fade, slide left, slide right, or no transitions
- 📐 **Flexible Aspect Ratios**: Auto-detect from first image or use standard ratios (16:9, 4:3, 1:1, 9:16)
- 🎯 **High Quality Output**: Support for 720p, 1080p, 1440p, and 4K resolutions
- ⏱️ **Customizable Timing**: Set duration per image from 0.1 to 10 seconds
- 🎥 **Multiple Frame Rates**: Choose from 24, 30, or 60 fps
- 🔧 **Smart Image Processing**: Automatic resizing and letterboxing to maintain aspect ratios

## Usage

### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `images` | List[File] | Required | List of 2-50 images to create slideshow from |
| `duration_per_image` | Float | 1.0 | Duration each image is displayed (0.1-10.0 seconds) |
| `aspect_ratio` | String | "auto" | Video aspect ratio: `auto`, `16:9`, `4:3`, `1:1`, `9:16` |
| `resolution` | String | "720p" | Output resolution: `720p`, `1080p`, `1440p`, `4k` |
| `transition_type` | String | "none" | Transition effect: `none`, `fade`, `slide_left`, `slide_right` |
| `frame_rate` | Integer | 30 | Output frame rate: `24`, `30`, `60` fps |

### API Example

```python
import replicate

output = replicate.run(
    "your-username/image-to-video-slideshow",
    input={
        "images": [
            open("image1.jpg", "rb"),
            open("image2.jpg", "rb"),
            open("image3.jpg", "rb")
        ],
        "duration_per_image": 2.5,
        "aspect_ratio": "16:9",
        "resolution": "1080p",
        "transition_type": "fade",
        "frame_rate": 30
    }
)
```

### cURL Example

```bash
curl -s -X POST \
  -H "Authorization: Token $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "your-model-version-hash",
    "input": {
      "images": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
      "duration_per_image": 2.0,
      "aspect_ratio": "16:9",
      "resolution": "1080p",
      "transition_type": "fade",
      "frame_rate": 30
    }
  }' \
  https://api.replicate.com/v1/predictions
```

## Aspect Ratios and Resolutions

### Aspect Ratio Options
- **auto**: Uses the aspect ratio of the first uploaded image
- **16:9**: Widescreen (landscape)
- **4:3**: Standard (landscape)
- **1:1**: Square
- **9:16**: Vertical (portrait)

### Resolution Guide
| Resolution | Dimensions |
|------------|------------|
| 720p | 1280×720 (16:9), varies for other ratios |
| 1080p | 1920×1080 (16:9), varies for other ratios |
| 1440p | 2560×1440 (16:9), varies for other ratios |
| 4k | 3840×2160 (16:9), varies for other ratios |

*Note: When using "auto" aspect ratio, the width is calculated to maintain the original image proportions.*

## Transition Effects

### Available Transitions
- **none**: Instant cut between images
- **fade**: Smooth crossfade between images
- **slide_left**: Current image slides left, next slides in from right
- **slide_right**: Current image slides right, next slides in from left

All transitions use 15 frames (0.5 seconds at 30fps) for smooth motion.

## Image Processing

The model automatically:
1. **Converts images to RGB** format
2. **Resizes images** to fit the target video dimensions
3. **Maintains aspect ratios** by adding letterboxing (black bars) when needed
4. **Centers images** within the video frame
5. **Optimizes quality** using high-quality JPEG compression and H.264 encoding

## Output

- **Format**: MP4 video file
- **Codec**: H.264 with yuv420p pixel format
- **Optimization**: Fast start enabled for web streaming
- **Quality**: CRF 23 (high quality, reasonable file size)

## Development

### Local Setup

1. Install Cog:
```bash
sudo curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_$(uname -s)_$(uname -m)
sudo chmod +x /usr/local/bin/cog
```

2. Run predictions locally:
```bash
cog predict -i images=@image1.jpg,@image2.jpg,@image3.jpg
```

## License

This project is open source. Please check the repository for license details. 