#---------------------------------------embedding_database.pt---------------------------------------
import torch

# Load the file
# path = "D:/data_for_california_fish/data_train.json_embedding_dep_fixed.pt"
path = "D:/data_for_california_fish/embedding_database.pt"
embedding_data = torch.load(path, map_location=torch.device('cpu'))

# Check the type of object
print(type(embedding_data))

# If it's a dictionary
if isinstance(embedding_data, dict):
    for key, value in embedding_data.items():
        print(f"Key: {key}, Type: {type(value)}, Shape: {getattr(value, 'shape', None)}")

# If it's a list
elif isinstance(embedding_data, list):
    print(f"List length: {len(embedding_data)}")
    print(f"First item: {embedding_data[0]}")

# If it's a tensor
elif isinstance(embedding_data, torch.Tensor):
    print(f"Tensor shape: {embedding_data.shape}")

# Show sample data
print(embedding_data[list(embedding_data.keys())[0]])  # If it's a dict



#---------------------------------------classification_model.ts---------------------------------------
# import torch

# # Path to your TorchScript model
# model_path = "D:/Fishing-AI/fishai_backend/cache/models/classification_model.ts"

# # Load the model
# model = torch.jit.load(model_path, map_location=torch.device("cpu"))

# # Print the model's architecture (if available)
# print("\n=== MODEL STRUCTURE ===")
# print(model.code)

# # Optional: Print the internal graph
# print("\n=== MODEL GRAPH ===")
# print(model.graph)


#---------------------------------------segmentation_model.ts---------------------------------------
# import torch
# import numpy as np
# import matplotlib.pyplot as plt
# from PIL import Image

# model = torch.jit.load("D:/Fishing-AI/fishai_backend/cache/models/segmentation_model.ts", map_location='cpu')
# model.eval()

# dummy_input = torch.randn(1, 3, 224, 224)
# with torch.no_grad():
#     output = model(dummy_input)
#     prob_map = torch.sigmoid(output)
#     mask = (prob_map > 0.5).float()

# mask_np = mask.squeeze().cpu().numpy()
# img = Image.fromarray((mask_np * 255).astype(np.uint8))
# img.save("segmentation_result.png")
