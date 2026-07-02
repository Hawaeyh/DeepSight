import timm


def create_binary_model():

    model = timm.create_model(
        "efficientnet_b0",
        pretrained=False,
        num_classes=2,
    )

    return model


def create_multiclass_model():

    model = timm.create_model(
        "efficientnet_b0",
        pretrained=False,
        num_classes=8,
    )

    return model