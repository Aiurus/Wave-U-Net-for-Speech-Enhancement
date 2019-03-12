import argparse
import json
import os
import torch
from torch.utils.data import DataLoader

from data.train_dataset import TrainDataset
from models.unet import UNet
from trainer.trainer import Trainer


def main(config, resume):
    train_data_args = config["train_data_loader"]
    train_dataset = TrainDataset(
        dataset_dir=train_data_args["dataset_dir"],
        limit=train_data_args["limit"],
        offset=train_data_args["offset"]
    )

    train_data_loader = DataLoader(
        dataset=train_dataset,
        batch_size=train_data_args["batch_size"],
        num_workers = train_data_args["num_workers"],
        shuffle = train_data_args["shuffle"],
        pin_memory=True
    )

    model = UNet()

    optimizer = torch.optim.Adam(
        params=model.parameters(),
        lr=config["optimizer"]["lr"],
        betas=(config["optimizer"]["b1"], 0.999)
    )

    trainer = Trainer(
        config=config,
        resume=resume,
        model=model,
        optim=optimizer,
        train_dl=train_data_loader,
        validation_dl=None
    )

    trainer.train()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UNet For Speech Enhancement')
    parser.add_argument("-c", "--config", default="./config/train_config.json", type=str, help="训练配置文件")
    parser.add_argument('-d', '--device', default=None, type=str, help="indices of GPUs to enable，e.g. '1,2,3'")
    parser.add_argument("-r", "--resume", action="store_true", help="是否从最近的一个断点处继续训练")
    args = parser.parse_args()

    if args.device:
        os.environ["CUDA_VISIBLE_DEVICES"] = args.device

    # load config file
    config = json.load(open(args.config))

    main(config, resume=args.resume)