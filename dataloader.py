import os
import csv
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
from PIL import Image

class DHF1KDataset(Dataset):
    def __init__(self, path_data, len_snippet, mode="train"):
        self.path_data = path_data
        self.len_snippet = len_snippet
        self.mode = mode
        self.img_transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225]
            )
        ])
        if self.mode == "train" or self.mode=="val":
            self.video_names = os.listdir(path_data)
            self.list_num_frame = [len(os.listdir(os.path.join(path_data,d,'images'))) for d in self.video_names]
        else:
            self.list_num_frame = []
            for v in os.listdir(path_data):
                for i in range(0, len(os.listdir(os.path.join(path_data,v,'images')))-self.len_snippet):
                    self.list_num_frame.append((v, i))

    def __len__(self):
        return len(self.list_num_frame)

    def __getitem__(self, idx):
        if self.mode == "train" or self.mode == "val":
            file_name = self.video_names[idx]
            start_idx = np.random.randint(0, self.list_num_frame[idx]-self.len_snippet+1)
        else:
            (file_name, start_idx) = self.list_num_frame[idx]

        path_clip = os.path.join(self.path_data, file_name, 'images')
        path_annt = os.path.join(self.path_data, file_name, 'maps')

        clip_img = []
        for i in range(self.len_snippet):
            img = Image.open(os.path.join(path_clip, '%04d.png'%(start_idx+i+1))).convert('RGB')
            clip_img.append(self.img_transform(img))
            
        clip_img = torch.FloatTensor(torch.stack(clip_img, dim=0))

        gt = np.array(Image.open(os.path.join(path_annt, '%04d.png'%(start_idx+self.len_snippet))).convert('L'))
        gt = gt.astype('float')
        gt = cv2.resize(gt, (256,256))
        if np.max(gt) > 1.0:
            gt = gt / 255.0

        return clip_img, torch.FloatTensor(gt)
