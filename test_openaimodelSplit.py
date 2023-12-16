import torch
from openaimodelSplit import AttentionPool2d

def test_attention_pool2d_invalid_input():
    # Test the AttentionPool2d layer with invalid input dimensions
    spacial_dim = 16
    embed_dim = 512
    num_heads_channels = 64
    attention_pool = AttentionPool2d(spacial_dim, embed_dim, num_heads_channels)

    # Create an invalid input tensor of shape (batch_size, channels, height)
    # Missing the width dimension
    batch_size = 4
    channels = embed_dim
    height = spacial_dim
    invalid_input = torch.randn(batch_size, channels, height)

    try:
        # Attempt to perform the forward pass
        output = attention_pool(invalid_input)
    except Exception as e:
        assert isinstance(e, ValueError), "Expected a ValueError for invalid input dimensions"

def test_attention_pool2d_output_values():
    # Test the AttentionPool2d layer to ensure it produces non-zero output
    spacial_dim = 16
    embed_dim = 512
    num_heads_channels = 64
    attention_pool = AttentionPool2d(spacial_dim, embed_dim, num_heads_channels)

    # Create a dummy input tensor of shape (batch_size, channels, height, width)
    batch_size = 4
    channels = embed_dim
    height = spacial_dim
    width = spacial_dim
    dummy_input = torch.randn(batch_size, channels, height, width)

    # Perform the forward pass
    output = attention_pool(dummy_input)

    # Check that the output contains non-zero values
    assert torch.any(output != 0), "Expected the output to contain non-zero values"
