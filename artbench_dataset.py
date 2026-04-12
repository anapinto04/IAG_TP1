import os
import pickle
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image
from torch.utils.data import Dataset


DATASET_PATH = Path("data/artbench-10-python/artbench-10-batches-py")


def download_artbench(project_dir=None):
    print("A iniciar download do ArtBench...")

    project_dir = Path.cwd() if project_dir is None else Path(project_dir)
    kaggle_json = project_dir / "kaggle.json"
    if not kaggle_json.exists():
        raise FileNotFoundError(f"kaggle.json nao encontrado em: {kaggle_json}")

    subprocess.run([sys.executable, "-m", "pip", "install", "kaggle"], check=True)

    data_dir = project_dir / "data"
    data_dir.mkdir(exist_ok=True)

    os.environ["KAGGLE_CONFIG_DIR"] = str(project_dir)

    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(
        "alexanderliao/artbench10",
        path=str(data_dir),
        unzip=False,
        quiet=False,
    )

    print("A extrair dataset...")
    with zipfile.ZipFile(data_dir / "artbench10.zip", "r") as zip_ref:
        zip_ref.extractall(data_dir)

    print("Dataset pronto em: data/artbench-10-python e data/artbench-10-binary")


class ArtBenchDataset(Dataset):
    def __init__(self, root=DATASET_PATH, transform=None, train=True):
        self.root = Path(root)
        self.transform = transform
        self.train = train

        if not self.root.exists():
            raise FileNotFoundError(f"Dataset nao encontrado em: {self.root.resolve()}")

        meta_path = self.root / "meta"
        with open(meta_path, "rb") as handle:
            meta = pickle.load(handle, encoding="bytes")

        self.classes = meta.get("styles")
        if self.classes is None:
            self.classes = meta.get(b"styles")
        if self.classes is None:
            raise KeyError("A chave 'styles' nao foi encontrada no ficheiro meta.")

        self.classes = [
            style.decode("utf-8") if isinstance(style, bytes) else str(style)
            for style in self.classes
        ]
        self.class_to_idx = {name: index for index, name in enumerate(self.classes)}

        batch_names = [f"data_batch_{index}" for index in range(1, 6)] if train else ["test_batch"]
        images = []
        labels = []

        for batch_name in batch_names:
            batch_path = self.root / batch_name
            with open(batch_path, "rb") as handle:
                batch = pickle.load(handle, encoding="bytes")

            batch_data = batch.get("data")
            if batch_data is None:
                batch_data = batch.get(b"data")

            batch_labels = batch.get("labels")
            if batch_labels is None:
                batch_labels = batch.get(b"labels")

            if batch_data is None or batch_labels is None:
                raise KeyError(f"O ficheiro {batch_name} nao tem o formato esperado.")

            images.append(batch_data)
            labels.extend(batch_labels)

        self.data = np.concatenate(images, axis=0).reshape(-1, 3, 32, 32)
        self.data = np.transpose(self.data, (0, 2, 3, 1))
        self.labels = [int(label) for label in labels]
        self.samples = list(enumerate(self.labels))

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        image = Image.fromarray(self.data[index])
        label = self.labels[index]

        if self.transform is not None:
            image = self.transform(image)

        return image, label