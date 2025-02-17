import os
import tensorflow as tf
import pickle

# _自定义包
import data_utils
import data_loader
import model_utils

flags = tf.app.flags

# 训练相关的
flags.DEFINE_boolean('train', True, '是否开始训练')
flags.DEFINE_boolean('clean', True, '是否清理临时文件')

# 配置相关
flags.DEFINE_integer('seg_dim', 20, 'seg embedding size')
flags.DEFINE_integer('word_dim', 120, 'word embedding')
flags.DEFINE_integer('lstm_dim', 120, 'Num of hidden unis in lstm')
flags.DEFINE_string('tag_schema', 'BIOES', '编码方式')

# 训练相关
flags.DEFINE_float('clip', 5, 'Grandient clip')
flags.DEFINE_float('dropout', 0.5, 'Dropout rate')
flags.DEFINE_integer('batch_size', 120, 'batch_size')
flags.DEFINE_float('lr', 0.001, 'learning rate')
flags.DEFINE_string('optimizer', 'adam', '优化器')
flags.DEFINE_boolean('pre_emb', True, '是否使用预训练')

flags.DEFINE_integer('max_epoch', 100, '最大轮训次数')
flags.DEFINE_integer('setps_chech', 100, 'steps per checkpoint')
flags.DEFINE_string('ckpt_path', os.path.join('modelfile', 'ckpt'), '保存模型的位置')
flags.DEFINE_string('log_file', 'train.log', '训练过程中日志')
flags.DEFINE_string('map_file', 'maps.pkl', '存放字典映射及标签映射')
flags.DEFINE_string('vocab_file', 'vocab.json', '字向量')
flags.DEFINE_string('config_file', 'config_file', '配置文件')
flags.DEFINE_string('result_path', 'result', '结果路径')
flags.DEFINE_string('emb_file', os.path.join('data', 'wiki_100.utf8'), '词向量文件路径')
flags.DEFINE_string('train_file', os.path.join('data', 'ner.train'), '训练数据路径')
flags.DEFINE_string('dev_file', os.path.join('data', 'ner.dev'), '校验数据路径')
flags.DEFINE_string('test_file', os.path.join('data', 'ner.test'), '测试数据路径')

FLAGS = tf.app.flags.FLAGS
assert FLAGS.clip < 5.1, '梯度裁剪不能过大'
assert 0 < FLAGS.dropout < 1, 'dropout必须在0和1之间'
assert FLAGS.lr > 0, 'lr 必须大于0'
assert FLAGS.optimizer in ['adam', 'sgd', 'adagrad'], '优化器必须在adam, sgd, adagrad'


def train():
    # 1、加载数据集
    train_sentences = data_loader.load_sentences(FLAGS.train_file)
    dev_sentences = data_loader.load_sentences(FLAGS.dev_file)
    test_sentences = data_loader.load_sentences(FLAGS.test_file)

    # 2、转换编码 BIO->BIOES
    data_loader.update_tag_scheme(train_sentences, FLAGS.tag_schema)
    data_loader.update_tag_scheme(dev_sentences, FLAGS.tag_schema)
    data_loader.update_tag_scheme(test_sentences, FLAGS.tag_schema)

    # 3、创建单词映射与标签映射
    if not os.path.isfile(FLAGS.map_file):
        _, word_to_id, id_to_word = data_loader.word_mapping(train_sentences)
        _, tag_to_id, id_to_tag = data_loader.tag_mapping(train_sentences)

        with open(FLAGS.map_file, "wb") as f:
            # 序列化pickle.dump(obj, file, [,protocol]),,序列化对象，将对象obj保存到文件file中去。
            pickle.dump([word_to_id, id_to_word, tag_to_id, id_to_tag], f)
    else:
        # 反序列化对象，将文件中的数据解析为一个python对象。file中有read()接口和readline()接口
        with open(FLAGS.map_file, "rb") as f:
            word_to_id, id_to_word, tag_to_id, id_to_tag = pickle.load(f)

    # 4、数据预处理
    train_data = data_loader.prepare_dataset(
        train_sentences, word_to_id, tag_to_id
    )

    dev_data = data_loader.prepare_dataset(
        dev_sentences, word_to_id, tag_to_id
    )

    test_data = data_loader.prepare_dataset(
        test_sentences, word_to_id, tag_to_id
    )

    model_utils.make_path(FLAGS)

    config = model_utils.config_model(FLAGS, word_to_id, tag_to_id)


def main(_):
    if FLAGS.train:
        train()
    else:
        pass


if __name__ == "__main__":
    tf.app.run(main)
