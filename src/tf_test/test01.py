import os
import tensorflow as tf

graph = tf.Graph()

with graph.as_default():
    a = tf.constant(3, name="a")
    b = tf.constant(5, name="b")
    x = tf.add(a, b, name="add")

with tf.Session(graph=graph) as session:
    writer = tf.summary.FileWriter(os.environ["TMP_PATH"] + "/tf_graphs", session.graph)
    print(session.run(x))

writer.close()
