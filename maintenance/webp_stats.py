import os
import statistics


def get_webp_sizes(base_directory):
    # List to hold sizes of image.webp files
    file_sizes = []

    # Loop through the directories in the base directory
    for segment in os.listdir(base_directory):
        segment_path = os.path.join(base_directory, segment)

        # Check if it's a directory and contains image.webp
        if os.path.isdir(segment_path) and "image.webp" in os.listdir(segment_path):
            image_path = os.path.join(segment_path, "image.webp")

            # Get size of the image.webp and append to the list
            file_size = os.path.getsize(image_path)
            file_sizes.append(file_size)

    return file_sizes


base_directory = "storage/segments"

# Get sizes of all image.webp files
sizes = get_webp_sizes(base_directory)

# Calculate stats
if sizes:
    avg_size = statistics.mean(sizes)
    median_size = statistics.median(sizes)
    std_dev = statistics.stdev(sizes) if len(sizes) > 1 else 0
    min_size = min(sizes)
    max_size = max(sizes)

    print(f"\nAverage size: {avg_size:.2f} bytes")
    print(f"Median size: {median_size:.2f} bytes")
    print(f"Standard Deviation: {std_dev:.2f} bytes")
    print(f"Min size: {min_size} bytes")
    print(f"Max size: {max_size} bytes\n")
else:
    print("No image.webp files found in the specified directory.")
