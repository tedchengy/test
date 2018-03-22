# coding:utf-8
import random
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from PIL import Image
from captcha.image import ImageCaptcha


number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


# 从number集合随机获取要是别的验证码数字集合
def random_captcha_text(captcha_set=number, captcha_size=4):
    captcha_text = []
    for i in range(captcha_size):
        captcha_text.append(random.choice(captcha_set))
    return captcha_text


# 以字符串形式返回待识别的数字集合，返回图片60*160的RGB色集合
def gen_captcha_text_image():
    image = ImageCaptcha()
    captcha_text = random_captcha_text()
    captcha_text = ''.join(captcha_text)
    captcha = image.generate(captcha_text)
    captcha_image = Image.open(captcha)
    captcha_image = np.array(captcha_image)
    return captcha_text, captcha_image


# 转变图片格式
def convert2gray(img):
    if len(img.shape) > 2:
        r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray
    else:
        return img


# 将正确结果的文本转化为4*10的一维向量，每10个中有一个1，代表正确结果
def text2vec(text):
    text_len = len(text)
    if text_len > max_captcha:
        raise ValueError("验证码最长4个字符")
    vector = np.zeros(max_captcha * char_set_len)

    def char2pos(c):
        if ord(c) < 48 | ord(c) > 57:
            raise ValueError(c+"不在1-9之间")
        k = ord(c) - 48
        return k

    for i, c in enumerate(text):
        idx = i * char_set_len + char2pos(c)
        vector[idx] = 1
    return vector


# 生成1维x,y数据
def get_next_batch(batch_size=128):
    batch_x = np.zeros([batch_size, image_weight * image_height])
    batch_y = np.zeros([batch_size, max_captcha * char_set_len])

    def wrap_gen_captcha_text_and_image():
        while True:
            text, image = gen_captcha_text_image()
            if image.shape == (60, 160, 3):
                return text, image
    for i in range(batch_size):
        text, image = wrap_gen_captcha_text_and_image()
        image = convert2gray(image)

        batch_x[i, :] = image.flatten() / 255
        batch_y[i, :] = text2vec(text)
        return batch_x, batch_y


# 卷积模型
def cnn_structure():
    x = tf.reshape(X, shape=[-1, image_height, image_weight, 1])

    # 第一次卷积，池化
    wc1 = tf.Variable(tf.random_normal([3, 3, 1, 32]))
    bc1 = tf.Variable(tf.random_normal([32]))
    conv1 = tf.nn.conv2d(x, wc1, strides=[1, 1, 1, 1], padding="SAME")
    conv1 = tf.nn.relu(tf.nn.bias_add(conv1, bc1))
    pool1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")
    pool1 = tf.nn.dropout(pool1, keepratio)

    # 第二次卷积，池化
    wc2 = tf.Variable(tf.random_normal([3, 3, 32, 64]))
    bc2 = tf.Variable(tf.random_normal([64]))
    conv2 = tf.nn.conv2d(pool1, wc2, strides=[1, 1, 1, 1], padding="SAME")
    conv2 = tf.nn.relu(tf.nn.bias_add(conv2, bc2))
    pool2 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")
    pool2 = tf.nn.dropout(pool2, keepratio)

    # 第三次卷积，池化
    wc3 = tf.Variable(tf.random_normal([3, 3, 64, 128]))
    bc3 = tf.Variable(tf.random_normal([128]))
    conv3 = tf.nn.conv2d(pool2, wc3, strides=[1, 1, 1, 1], padding="SAME")
    conv3 = tf.nn.relu(tf.nn.bias_add(conv3, bc3))
    pool3 = tf.nn.max_pool(conv3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")
    pool3 = tf.nn.dropout(pool3, keepratio)

    # 全连接层
    wd1 = tf.Variable(tf.random_normal([8*20*128, 1024]))
    bd1 = tf.Variable(tf.random_normal([1024]))
    # 输出转为一维向量
    dense = tf.reshape(pool3, [-1, wd1.get_shape().as_list()[0]])
    fcl = tf.nn.relu(tf.add(tf.matmul(dense, wd1), bd1))
    fcl = tf.nn.dropout(fcl, keepratio)

    wout = tf.Variable(tf.random_normal([1024, out_num]))
    bout = tf.Variable(tf.random_normal([out_num]))
    out = tf.add(tf.matmul(fcl, wout), bout)
    return out


# 训练卷积神经网络
def train_cnn():
    output = cnn_structure()
    cost = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=output, labels=Y))
    # cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=output, labels=Y))
    optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(cost)
    predict = tf.reshape(output, [-1, max_captcha, char_set_len])
    max_idx_p = tf.argmax(predict, 2)
    max_idx_l = tf.argmax(tf.reshape(Y, [-1, max_captcha, char_set_len]), 2)
    correct_pred = tf.equal(max_idx_p, max_idx_l)
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

    saver = tf.train.Saver()

    with tf.Session() as sess:
        init = tf.global_variables_initializer()
        sess.run(init)
        step = 0
        while True:
            batch_x, batch_y = get_next_batch(100)
            sess.run([optimizer, cost], feed_dict={X: batch_x, Y: batch_y, keepratio: 0.75})
            if step % 10 == 0:
                batch_x_test, batch_y_test = get_next_batch(100)
                acc = sess.run(accuracy, feed_dict={X: batch_x_test, Y: batch_y_test, keepratio: 1.})
                print(step, acc)
                if acc > 0.99:
                    saver.save(sess, "./model/crack_capcha.model", global_step=step)
                    break
            step += 1


def crack_captcha(captcha_image):
    output = cnn_structure()

    saver = tf.train.Saver()
    with tf.Session() as sess:
        saver.restore(sess, "./model/crack_capcha.model-1200")

        predict = tf.argmax(tf.reshape(output, [-1, max_captcha, char_set_len]), 2)
        text_list = sess.run(predict, feed_dict={X: [captcha_image], keepratio: 1.})
        text = text_list[0].tolist()
        return text

if __name__ == '__main__':
    train = 0
    if train == 0:
        text, image = gen_captcha_text_image()
        print("验证码大小：", image.shape)  # (60,160,3)

        image_height = 60
        image_weight = 160
        max_captcha = len(text)
        print("验证码文本最长字符数", max_captcha)
        char_set = number
        char_set_len = len(char_set)

        out_num = max_captcha * char_set_len
        keepratio = tf.placeholder(tf.float32)
        X = tf.placeholder(tf.float32, [None, image_height * image_weight])
        Y = tf.placeholder(tf.float32, [None, max_captcha * char_set_len])
        train_cnn()

    if train == 1:
        image_height = 60
        image_width = 160
        char_set = number
        char_set_len = len(char_set)

        text, image = gen_captcha_text_image()

        f = plt.figure()
        ax = f.add_subplot(111)
        ax.text(0.1, 0.9, text, ha='center', va='center', transform=ax.transAxes)
        plt.imshow(image)

        max_captcha = len(text)
        image = convert2gray(image)
        image = image.flatten() / 255

        keepratio = tf.placeholder(tf.float32)
        X = tf.placeholder(tf.float32, [None, image_height * image_weight])
        Y = tf.placeholder(tf.float32, [None, max_captcha * char_set_len])

        predict_text = crack_captcha(image)
        print("正确: {}  预测: {}".format(text, predict_text))

        plt.show()
