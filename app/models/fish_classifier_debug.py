import torch
import numpy as np
import torchvision.transforms as T
from util import load_classification_model, load_embedding_data

# Threshold for prediction acceptance
THRESHOLD = 4.0

# Load models and embeddings
model = load_classification_model()
embedding_tensor, labels, filenames, uuids, ann_ids, label_dict = load_embedding_data()

# Preprocessing transform
transform = T.Compose([
    T.Resize([224, 224]),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def classify(image):
    print("[DEBUG] Running classify()")
    image_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(image_tensor)

    # Support for torch.jit traced model returning a tuple
    if isinstance(output, tuple):
        output = output[0]
    output = output.squeeze(0)  # shape [128]

    # Calculate L2 distances
    distances = torch.norm(embedding_tensor - output, dim=1)
    min_val, min_idx = torch.min(distances, dim=0)
    print(f"[DEBUG] Closest distance: {min_val.item():.4f} (Index: {min_idx})")

    if min_val.item() > THRESHOLD:
        print("[DEBUG] No match passed threshold")
        return []

    predicted_label = labels[min_idx.item()]
    label_info = label_dict.get(str(predicted_label), {})
    print(f"[DEBUG] Predicted: {label_info} with distance {min_val.item():.4f}")

    return [label_info]