import os

import numpy as np
import tensorflow as tf

from flowerTrain import input_data
from flowerTrain import model


class Train:
	path, train_dir, logs_train_dir = None, None, None

	def __init__(self):
		self.path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
		self.train_dir = self.path + '/input_data'  # 训练样本的读入路径
		self.logs_train_dir = self.path + '/save'  # logs存储路径

	def train(self, BATCH_SIZE=20, MAX_STEP=1000, learning_rate=0.0001):
		# 变量声明
		N_CLASSES = 4  # 四种花类型
		IMG_W = 64  # resize图像，太大的话训练时间久
		IMG_H = 64
		CAPACITY = 200
		# 获取批次batch
		# train, train_label = input_data.get_files(train_dir)
		train, train_label, val, val_label = input_data.get_files(self.train_dir, 0.3)
		# 训练数据及标签
		train_batch, train_label_batch = input_data.get_batch(train, train_label, IMG_W, IMG_H, BATCH_SIZE, CAPACITY)
		# 测试数据及标签
		val_batch, val_label_batch = input_data.get_batch(val, val_label, IMG_W, IMG_H, BATCH_SIZE, CAPACITY)

		# 训练操作定义
		train_logits = model.inference(train_batch, BATCH_SIZE, N_CLASSES)
		train_loss = model.losses(train_logits, train_label_batch)
		train_op = model.trainning(train_loss, learning_rate)
		train_acc = model.evaluation(train_logits, train_label_batch)

		# 测试操作定义
		test_logits = model.inference(val_batch, BATCH_SIZE, N_CLASSES)
		test_loss = model.losses(test_logits, val_label_batch)
		test_acc = model.evaluation(test_logits, val_label_batch)

		# 这个是log汇总记录
		summary_op = tf.summary.merge_all()

		# 产生一个会话
		sess = tf.Session()
		# 产生一个writer来写log文件
		train_writer = tf.summary.FileWriter(self.logs_train_dir, sess.graph)
		# 产生一个saver来存储训练好的模型
		saver = tf.train.Saver()
		# 所有节点初始化
		sess.run(tf.initialize_all_variables())
		# 队列监控
		coord = tf.train.Coordinator()
		threads = tf.train.start_queue_runners(sess=sess, coord=coord)

		# 进行batch的训练
		try:
			print('批次为：{}，步数为：{}，学习率为：{}'.format(BATCH_SIZE, MAX_STEP, learning_rate))
			# 执行MAX_STEP步的训练，一步一个batch
			for step in np.arange(MAX_STEP + 1):
				if coord.should_stop():
					break
				_, tra_loss, tra_acc = sess.run([train_op, train_loss, train_acc])

				# 每隔50步打印一次当前的loss以及acc，同时记录log，写入writer
				if step % 10 == 0:
					print('步数：%d, loss：%.2f, 训练准确率：%.2f%%' % (step, tra_loss, tra_acc * 100.0))
					summary_str = sess.run(summary_op)
					train_writer.add_summary(summary_str, step)
				# 每隔100步，保存一次训练好的模型
				if (step) == MAX_STEP:
					checkpoint_path = os.path.join(self.logs_train_dir, 'model.ckpt')
					saver.save(sess, checkpoint_path, global_step=step)

		except tf.errors.OutOfRangeError:
			print('到达训练上限，训练完成')

		finally:
			coord.request_stop()


if __name__ == '__main__':
	Train().train()
