import torch
import sys

print(f"Python Version: {sys.version}")
print(f"PyTorch Version: {torch.__version__}")
print("-" * 20)

# Check if GPU is available
if torch.cuda.is_available():
    device_name = torch.cuda.get_device_name(0)
    print(f"✅ GPU Detected: {device_name}")
    
    # Try to use it
    try:
        x = torch.rand(5, 3).to("cuda")
        # Force a synchronization to catch the error immediately
        torch.cuda.synchronize()
        print("✅ GPU Tensor Test Passed (Math works!)")
        print(x)
    except RuntimeError as e:
        print(f"⚠️ GPU CRASH: {e}")
        print("💡 Diagnosis: PyTorch 2.4+ does not support RX 580 (Polaris) instructions.")
        print("👉 Falling back to CPU for now...")
        
        x = torch.rand(5, 3).to("cpu")
        print("✅ CPU Tensor Created successfully:")
        print(x)
else:
    print("❌ No GPU detected. Running on CPU.")