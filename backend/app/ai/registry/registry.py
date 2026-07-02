from app.ai.registry.registry import MODEL_REGISTRY

binary_model.load_state_dict(
    torch.load(
        MODEL_REGISTRY["binary"]["path"],
        map_location=DEVICE,
    )
)

multiclass_model.load_state_dict(
    torch.load(
        MODEL_REGISTRY["multiclass"]["path"],
        map_location=DEVICE,
    )
)