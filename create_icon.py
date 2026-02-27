from PIL import Image, ImageDraw

# Create a 256x256 image with transparency
size = 256
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Colors - podcast microphone icon
mic_color = (52, 152, 219)  # Blue color similar to app
outline_color = (41, 128, 185)

# Draw microphone body (rounded rectangle)
mic_width = 80
mic_height = 140
mic_x = (size - mic_width) // 2
mic_y = 40

# Microphone capsule (top rounded part)
draw.ellipse([mic_x, mic_y, mic_x + mic_width, mic_y + 50], 
             fill=mic_color, outline=outline_color, width=4)

# Microphone body
draw.rectangle([mic_x, mic_y + 25, mic_x + mic_width, mic_y + mic_height],
               fill=mic_color, outline=outline_color, width=4)

# Bottom curve
draw.arc([mic_x, mic_y + mic_height - 30, mic_x + mic_width, mic_y + mic_height + 10],
         start=0, end=180, fill=outline_color, width=4)

# Stand arc
stand_y = mic_y + mic_height
arc_size = 60
draw.arc([mic_x + mic_width//2 - arc_size//2, stand_y, 
          mic_x + mic_width//2 + arc_size//2, stand_y + 40],
         start=0, end=180, fill=outline_color, width=4)

# Stand base
base_width = 100
base_x = (size - base_width) // 2
base_y = stand_y + 35
draw.line([base_x, base_y, base_x + base_width, base_y],
          fill=outline_color, width=8)

# Center line on mic (detail)
draw.line([size//2, mic_y + 30, size//2, mic_y + mic_height - 5],
          fill=(255, 255, 255, 100), width=3)

# Save as .ico with multiple sizes
img.save('podcast_icon.ico', format='ICO', 
         sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print("Icon created: podcast_icon.ico")
