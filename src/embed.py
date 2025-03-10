import os

import deeplake
from torch.utils.data import DataLoader

from utils import (
    get_args,
    get_dataset,
    Network,
    NetworkHandler
)

def main():
    arg_path = os.path.join("configs", "embed.yaml")
    args = get_args(arg_path)

    data_dir = os.path.join("..", "data")
    encoder_dir = os.path.join("..", "assets", "model-weights", "pre-trained-weights")

    dest_dir = os.path.join("..", "embeddings", args["dataset"], args["encoder"])
    os.makedirs(dest_dir, exist_ok=True)

    model = Network(args["encoder"], encoder_dir)
    network_handler = NetworkHandler(model)    
    embedding_dim = model.fc.head.in_features

    train_dataset = get_dataset(
        name=args["dataset"], 
        split="train", 
        data_dir=data_dir
    )
    
    test_dataset = get_dataset(
        name=args["dataset"], 
        split="val" if args["dataset"] != "gleason-grading" else "test", 
        data_dir=data_dir
    )

    train_loader = DataLoader(
        train_dataset, 
        batch_size=args["batch_size"], 
        shuffle=False
    )
    
    val_loader = DataLoader(
        test_dataset, 
        batch_size=args["batch_size"], 
        shuffle=False
    )

    train_ds = deeplake.create(os.path.join(dest_dir, "train"))
    val_ds = deeplake.create(os.path.join(
        dest_dir, 
        "val" if args["dataset"] != "gleason-grading" else "test"
        ))

    train_ds.add_column("embedding", dtype=deeplake.types.Embedding(embedding_dim))
    train_ds.add_column("label", dtype= deeplake.types.Int32)
    train_ds.add_column("file_key", dtype= deeplake.types.Int32)

    val_ds.add_column("embedding", dtype=deeplake.types.Embedding(embedding_dim))
    val_ds.add_column("label", dtype= deeplake.types.Int32)
    val_ds.add_column("file_key", dtype= deeplake.types.Int32)

    print("Training set")
    network_handler.extract_embeddings(train_loader, train_ds)

    print("\nValidation set")
    network_handler.extract_embeddings(val_loader, val_ds)

if __name__ == "__main__":
    main()