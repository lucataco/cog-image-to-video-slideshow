from cog import BasePredictor, Input, Path as CogPath
import tempfile
import subprocess
from typing import List
from pathlib import Path
from PIL import Image
import cv2
import numpy as np

class Predictor(BasePredictor):
    def predict(
        self,
        images: List[CogPath] = Input(
            description="List of images to create slideshow from. Upload 2-50 images.",
            default=None
        ),
        duration_per_image: float = Input(
            description="Duration each image is displayed (in seconds)",
            default=1.0,
            ge=0.1,
            le=10.0
        ),
        aspect_ratio: str = Input(
            description="Video aspect ratio - 'auto' uses the first image's dimensions",
            default="auto",
            choices=["auto", "16:9", "4:3", "1:1", "9:16"]
        ),
        resolution: str = Input(
            description="Output video resolution (height for auto aspect ratio)",
            default="720p",
            choices=["720p", "1080p", "1440p", "4k"]
        ),
        transition_type: str = Input(
            description="Transition effect between images",
            default="none",
            choices=["none", "fade", "slide_left", "slide_right"]
        ),
        frame_rate: int = Input(
            description="Output video frame rate (fps)",
            default=30,
            choices=[24, 30, 60]
        )
    ) -> CogPath:
        """Create an MP4 video slideshow from a list of images"""
        
        if not images or len(images) < 2:
            raise ValueError("Please provide at least 2 images")
        
        if len(images) > 50:
            raise ValueError("Maximum 50 images allowed")
        
        # Determine video dimensions
        if aspect_ratio == "auto":
            # Use dimensions from first image
            first_img = Image.open(images[0])
            img_width, img_height = first_img.size
            
            # Scale to target resolution height
            height_map = {"720p": 720, "1080p": 1080, "1440p": 1440, "4k": 2160}
            target_height = height_map[resolution]
            
            # Calculate width maintaining aspect ratio
            aspect = img_width / img_height
            width = int(target_height * aspect)
            height = target_height
        else:
            # Use predefined aspect ratios
            height_map = {"720p": 720, "1080p": 1080, "1440p": 1440, "4k": 2160}
            height = height_map[resolution]
            
            aspect_ratios = {
                "16:9": 16/9,
                "4:3": 4/3, 
                "1:1": 1/1,
                "9:16": 9/16
            }
            width = int(height * aspect_ratios[aspect_ratio])
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Process and save images
            processed_images = []
            for i, image_path in enumerate(images):
                img = Image.open(image_path).convert('RGB')
                
                # Resize image to fit video dimensions while preserving aspect ratio
                img_aspect = img.size[0] / img.size[1]
                video_aspect = width / height
                
                if img_aspect > video_aspect:
                    # Image is wider - fit to width, pad height
                    new_width = width
                    new_height = int(width / img_aspect)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Create canvas and center image
                    canvas = Image.new('RGB', (width, height), (0, 0, 0))
                    paste_y = (height - new_height) // 2
                    canvas.paste(img, (0, paste_y))
                    img = canvas
                else:
                    # Image is taller - fit to height, pad width
                    new_height = height
                    new_width = int(height * img_aspect)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Create canvas and center image
                    canvas = Image.new('RGB', (width, height), (0, 0, 0))
                    paste_x = (width - new_width) // 2
                    canvas.paste(img, (paste_x, 0))
                    img = canvas
                
                # Save processed image
                output_path = temp_path / f"image_{i:04d}.jpg"
                img.save(output_path, "JPEG", quality=95)
                processed_images.append(output_path)
            
            # Create video frames
            video_frames = []
            transition_frames = 15 if transition_type != "none" else 0
            frames_per_image = int(duration_per_image * frame_rate)
            
            for i, img_path in enumerate(processed_images):
                current_img = cv2.imread(str(img_path))
                
                # Add main image frames
                for _ in range(frames_per_image - transition_frames):
                    video_frames.append(current_img)
                
                # Add transition frames (except for last image)
                if i < len(processed_images) - 1 and transition_type != "none":
                    next_img = cv2.imread(str(processed_images[i + 1]))
                    
                    if transition_type == "fade":
                        for j in range(transition_frames):
                            alpha = j / transition_frames
                            blended = cv2.addWeighted(current_img, 1 - alpha, next_img, alpha, 0)
                            video_frames.append(blended)
                    
                    elif transition_type == "slide_left":
                        for j in range(transition_frames):
                            offset = int((j / transition_frames) * width)
                            frame = np.zeros_like(current_img)
                            
                            # Current image sliding left
                            if offset < width:
                                frame[:, :width-offset] = current_img[:, offset:]
                            
                            # Next image sliding in from right
                            if offset > 0:
                                frame[:, width-offset:] = next_img[:, :offset]
                            
                            video_frames.append(frame)
                    
                    elif transition_type == "slide_right":
                        for j in range(transition_frames):
                            offset = int((j / transition_frames) * width)
                            frame = np.zeros_like(current_img)
                            
                            # Current image sliding right
                            if offset < width:
                                frame[:, offset:] = current_img[:, :width-offset]
                            
                            # Next image sliding in from left
                            if offset > 0:
                                frame[:, :offset] = next_img[:, width-offset:]
                            
                            video_frames.append(frame)
            
            # Write video using OpenCV
            output_path = temp_path / "slideshow.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, frame_rate, (width, height))
            
            for frame in video_frames:
                out.write(frame)
            out.release()
            
            # Convert to H.264 using FFmpeg for better compatibility
            final_output = temp_path / "final_slideshow.mp4"
            subprocess.run([
                'ffmpeg', '-i', str(output_path),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                str(final_output)
            ], check=True, capture_output=True)
            
            # Copy to output location
            output_video = Path(tempfile.mkdtemp()) / "slideshow.mp4"
            subprocess.run(['cp', str(final_output), str(output_video)], check=True)
            
            return CogPath(output_video)
