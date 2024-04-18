import os
import matplotlib.pyplot as plt
import edsr
from common import resolve_single
from utils import load_image
import numpy as np
import datetime
import cv2
import matplotlib
from PIL import Image

# Number of residual blocks
depth = 16
# Super-resolution factor
scale = 4
# Downgrade operator
downgrade = 'bicubic'
# Location of model weights (needed for demo)
weights_dir = f'weights/edsr-{depth}-x{scale}'
weights_file = os.path.join(weights_dir, 'weights.h5')
os.makedirs(weights_dir, exist_ok=True)
model = edsr.edsr(scale=scale, num_res_blocks=depth)
model.load_weights(weights_file)




def main(load_image_path, save_path, email):
    with Image.open(load_image_path) as img:
        if img.format != 'PNG':
            base = os.path.splitext(load_image_path)[0]
            new_path = f"{base}.png"
            img.save(new_path, 'PNG')
            load_image_path = new_path
    lr = load_image(load_image_path)
    # lr = cv2.imread(load_image_path ,cv2.IMREAD_UNCHANGED)
    # 如果图像是四通道的，去除透明度通道
    if lr.shape[2] == 4:
        lr = lr[:, :, :3]
    print("load successful")
    sr = resolve_single(model, lr)
    print("resolve successful")
    # sr_cv = sr.numpy()[..., ::-1]
    # cv2.imwrite(save_path, sr_cv)
    file_path = ""
    file_path = save_image(sr, save_path, email)
    print("Saved pic {}".format(save_path))
    return sr, file_path

def save_image(image, load_path, userEmail):
    # matplotlib.pyplot.imshow(image)
    """Saves an image to the specified path with a filename based on the userEmail and current time."""
    # 确保路径存在
    if not os.path.exists(load_path):
        os.makedirs(load_path)

    # 格式化当前时间
    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    userEmail_safe = userEmail.replace("@", "_").replace(".", "_")
    filename = f"{userEmail_safe}-{current_time}.jpg"

    # 完整的文件路径
    file_path = os.path.join(load_path, filename)
    # matplotlib.pyplot.imshow(image)
    # 删除批处理维度，并将像素值缩放到[0, 255]
    # image_np = image.numpy()
    # print(image_np.min(), image_np.max())
    # image = np.squeeze(image) * 255
    image = np.clip(image, 0, 255).astype(np.uint8)
    # matplotlib.pyplot.imshow(image)
    # plt.show()
    plt.imsave(file_path, image)
    # cv2.imwrite(file_path, image)
    print(file_path)
    return file_path


# main(load_image_path='demo/2.jpg', save_path="../static/result_picture", email="aaa@outlook.com")
# main(load_image_path='demo/S1.1.png', save_path="demo/2.png")