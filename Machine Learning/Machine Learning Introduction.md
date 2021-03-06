# Machine Learning - Introduction

Created by : Mr Dk.

2019 / 01 / 26 12:20

Ningbo, Zhejiang, China

---

<u>Understanding Machine Learning, From Theory to Algorithms</u>, _Shai Shalev-Shwartz_, _Shai Ben-David_

## What Is Learning?

>Machine Learning: we wish to program computers so that they can "learn" from input available to them. Roughly speaking, learning is the process of converting experience into expertise of knowledge. The input to a learning algorithm is training data, representing experience, and the output is some expertise, which usually takes the form of another computer program that perform some task.

---

## When Do We Need Machine Learning?

Two aspects of a given problem may call for the use of programs that learn and improve on the basis of their "experience": the problem's __complexity__ and the need for __adaptivity__.

### Tasks That Are Too Complex to Program

* _Tasks Performed by Animals/Humans:_
  * Not sufficiently elaborate to extract a well defined program
  * driving, speech recognition, image understanding
* _Tasks beyond Human Capabilities:_
  * The analysis of very large and complex data sets
  * Data archives that are too large and too complex for humans to make sense of
  * astronomical data, weather prediction, analysis of genomic data, Web search engines

### Adaptivity

* Many tasks change over time or from one user to another
  * decode handwritten text, spam detection programs, speech recognition programs

---

## Types of Learning

* Supervised versus Unsupervised

  >Supervised learning describes a scenario in which the "experience", a training example, contains significant information that is missing in the unseen "test examples" to which the learned expertise is to be applied. In this setting, the acquired expertise is aimed to predict that missing information for the test data. In such cases, we can think of the environment as a teacher that "supervises" the learner by providing the extra information (labels).
  >
  >In unsupervised leaning, however, there is no distinction between training and test data. The leaner processed input data with the goal of coming up with some summary, or compressed version of that data (like clustering).

* Active versus Passive Learners

  * Active - interacts with the environment at training time
  * Passive - observes the information provided by the environment (or the teacher) without influencing or directing it.

* Helpfulness of the Teacher

  * The training data is generated by some random process
  * The training data is generated by an adversarial "teacher"

* Online versus Batch Learning Protocol

  * Online - the learner has to respond online, throughout the learning process
  * Offline - the learner has large amounts of training data to play with before having to output conclusions

---

## Summary

虽然很抗拒 但还是不得不开始看机器学习的书了

全英文的 有点难度

需要极度专心

再后面还有偏数学的部分

真他妈讨厌啊......

---

