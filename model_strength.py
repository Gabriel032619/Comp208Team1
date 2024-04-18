# EDSR algorithm
import cv2
import tensorflow as tf


import os

from PIL import ImageEnhance

print(os.getcwd())

import strength.edsr as edsr
from strength.utils import load_image
# import cv2
def resolve_single(model, lr):
    return resolve(model, tf.expand_dims(lr, axis=0))[0]
def resolve(model, lr_batch):
    lr_batch = tf.cast(lr_batch, tf.float32)
    sr_batch = model(lr_batch)
    sr_batch = tf.clip_by_value(sr_batch, 0, 255)
    sr_batch = tf.round(sr_batch)
    sr_batch = tf.cast(sr_batch, tf.uint8)
    return sr_batch

# Number of residual blocks
depth = 16
# Super-resolution factor
scale = 4
# Downgrade operator
downgrade = 'bicubic'
# Location of model weights (needed for demo)
# print(os.getcwd())
weights_dir = f'weights/edsr-{depth}-x{scale}'
weights_file = os.path.join(weights_dir, 'weights.h5')
os.makedirs(weights_dir, exist_ok=True)
model = edsr.edsr(scale=scale, num_res_blocks=depth)
model.load_weights(weights_file)


def main(load_image_path, save_path):
    lr = load_image(load_image_path)
    if lr.shape[2] == 4:
        lr = lr[:, :, :3]
    print("load successful")
    sr = resolve_single(model, lr)
    print("resolve successful")
    sr_cv = sr.numpy()[..., ::-1]
    cv2.imwrite(save_path, sr_cv)
    print("Saved pic {}".format(save_path))
    enhancer = ImageEnhance.Color(sr_cv)
    sr_cv = enhancer.enhance(100)
    return sr_cv,save_path


# main(load_image_path='testPicture/2.jpg', save_path="static/result_picture/1.jpg")
# main(load_image_path='demo/S1.1.png', save_path="demo/2.png")

#
#
#
#
#
#
#
#
#
#
#
# def save_image(image, load_path, userEmail):
#     """Saves an image to the specified path with a filename based on the userEmail and current time."""
#     # 确保路径存在
#     # if not os.path.exists(load_path):
#     #     os.makedirs(load_path)
#     print("save path exist")
#     # 格式化当前时间
#     current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
#
#     userEmail_safe = userEmail.replace("@", "_").replace(".", "_")
#     filename = f"{userEmail_safe}-{current_time}.jpg"
#
#     # 完整的文件路径
#     file_path = os.path.join(load_path, filename)
#
#     # 删除批处理维度，并将像素值缩放到[0, 255]
#     image = np.squeeze(image) * 255
#     image = np.clip(image, 0, 255).astype(np.uint8)
#
#     # 使用PIL保存图片
#     plt.imsave(file_path, image)
#     print("well save")
#
#     return file_path
#
#
# def model_strength(load_image_path, save_path, userEmail):
#     save_path, sr_cv = main(load_image_path=load_image_path, save_path=save_path)
#     path = save_image(sr_cv, load_path=save_path, userEmail=userEmail)
#     return sr_cv, path
#
#
# model_strength("testPicture/flower.jpg",userEmail="aaa@outlook.com",save_path="static/result_picture")