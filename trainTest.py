import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import os.path

from PIL import Image
from flowerTrain import model

path = os.path.dirname(os.path.realpath(__file__))

# 获取一张图片
def get_one_image(train):
    # 输入参数：train,训练图片的路径
    # 返回参数：image，从训练图片中随机抽取一张图片
    n = len(train)
    ind = np.random.randint(0, n)
    img_dir = train[ind]  # 随机选择测试的图片

    img = Image.open(img_dir)
    plt.imshow(img)
    plt.show()
    image = np.array(img)
    return image


# 测试图片
def evaluate_one_image(image_array):
    with tf.Graph().as_default():
        BATCH_SIZE = 1
        N_CLASSES = 4

        image = tf.cast(image_array, tf.float32)
        image = tf.image.per_image_standardization(image)
        image = tf.reshape(image, [1, 64, 64, 3])

        logit = model.inference(image, BATCH_SIZE, N_CLASSES)

        logit = tf.nn.softmax(logit)

        logs_train_dir = path + '/save'

        x = tf.placeholder(tf.float32, shape=[64, 64, 3])

        saver = tf.train.Saver()

        with tf.Session() as sess:

            print("正在加载 CheckPoint")
            ckpt = tf.train.get_checkpoint_state(logs_train_dir)
            if ckpt and ckpt.model_checkpoint_path:
                global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
                saver.restore(sess, ckpt.model_checkpoint_path)
                print('数据加载成功, 总步数为%s' % global_step)
            else:
                print('未找到CheckPoint文件')

            prediction = sess.run(logit, feed_dict={x: image_array})
            max_index = np.argmax(prediction)
            if max_index == 0:
                result = '是玫瑰花的可能性为： {:.2%}'.format(prediction[:, 0][0])
            elif max_index == 1:
                result = '是郁金香的可能性为： {:.2%}'.format(prediction[:, 1][0])
            elif max_index == 2:
                result = '是蒲公英的可能性为： {:.2%}'.format(prediction[:, 2][0])
            else:
                result = '是向日葵的可能性为： {:.2%}'.format(prediction[:, 3][0])

            return result


# ------------------------------------------------------------------------

if __name__ == '__main__':
    img = Image.open(path + '/test_data/test1.jpg')
    plt.imshow(img)
    plt.show()
    imag = img.resize([64, 64])
    image = np.array(imag)
    print(evaluate_one_image(image))
