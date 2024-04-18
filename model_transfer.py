import os
from matplotlib import gridspec
import matplotlib.pylab as plt
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import datetime

# model from: https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2

def load_image(image_path, image_size=(256, 256), preserve_aspect_ratio=True):
    """Loads and preprocesses local images."""
    print(f"Loading image from path: {image_path}")
    # 读取本地图像文件
    img = tf.io.decode_image(
        tf.io.read_file(image_path),
        channels=3, dtype=tf.float32)
    print("ok load in load def")
    img = tf.image.resize(img, image_size, preserve_aspect_ratio=preserve_aspect_ratio)
    # 添加批处理维度并规范化到范围[0, 1]
    img = img[tf.newaxis, ...]
    return img


# 展示原始图，风格图，生成图，以及对应标题
def show_n(images, titles=('',)):
    n = len(images)
    image_sizes = [image.shape[1] for image in images]
    image_sizes_width = [image.shape[2] for image in images]
    w = (image_sizes[0] * 6) // image_sizes_width[0] * 2  # 乘以的倍数越多，图像越清晰，title看起来越小
    plt.figure(figsize=(w * n, w))
    gs = gridspec.GridSpec(1, n, width_ratios=image_sizes)
    for i in range(n):
        plt.subplot(gs[i])
        plt.imshow(images[i][0], aspect='equal')
        plt.axis('off')
        plt.title(titles[i] if len(titles) > i else '', fontsize=w * 5)  # title过小则加大倍数
    plt.show()


def show_final(image):
    height, width = image.shape[1], image.shape[2]
    # 计算figsize
    dpi = 100  # DPI可以根据需要调整
    figsize = width / dpi, height / dpi

    # 设置画布大小并显示图像
    plt.figure(figsize=figsize)
    plt.imshow(image[0])  # 图像具有额外的批处理维度,不可删
    plt.axis('off')  # 关闭坐标轴
    plt.show()




def save_image(image, load_path, userEmail):
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

    # 删除批处理维度，并将像素值缩放到[0, 255]
    image = np.squeeze(image) * 255
    image = np.clip(image, 0, 255).astype(np.uint8)

    # 使用PIL保存图片
    plt.imsave(file_path, image)

    return file_path


def main(content_image, style_image, load_path, userEmail, output_image_size=1024):
    print(f"Content image path: {content_image}")  # 打印以确认
    print(f"Style image path: {style_image}")      # 打印以确认
    # The content image size can be arbitrary.
    content_img_size = (output_image_size, output_image_size)
    # The style prediction model was trained with image size 256 and it's the
    # recommended image size for the style image (though, other sizes work as
    # well but will lead to different results).
    style_img_size = (256, 256)  # Recommended to keep it at 256.
    print("not load")
    content_image = load_image(content_image, content_img_size)
    print("ok load not pool")
    style_image = load_image(style_image, style_img_size)
    style_image = tf.nn.avg_pool(style_image, ksize=[3, 3], strides=[1, 1], padding='SAME')

    # 假设你的模型被下载并解压到了以下路径
    local_hub_model_path = 'models/transfer'

    # 使用 hub.load() 并提供本地路径而非 URL
    hub_module = hub.load(local_hub_model_path)

    # Stylize content image with given style image.
    # This is pretty fast within a few milliseconds on a GPU.
    outputs = hub_module(tf.constant(content_image), tf.constant(style_image))
    stylized_image = outputs[0]  # 结果图，不想要白边就直接return stylized_image
    path=save_image(stylized_image, load_path, userEmail=userEmail)

    return stylized_image,path


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 仅显示错误信息
# run
# main(content_image="testPicture/flower.jpg", style_image='testPicture/future.jpg', userEmail='isnova666@outlook.com',
     # load_path="result_picture", output_image_size=518)
