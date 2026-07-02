import torch

path = "app/models/production/binary/current_model.pth"

try:

    model = torch.load(
        path,
        map_location="cpu",
        weights_only=False
    )

    print(type(model))

except Exception as e:

    print(e)