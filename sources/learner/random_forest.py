################################################################################
#                                                                              #
#                          Random Forest Based Learner:                        #
#                                                                              #
################################################################################
#                                                                              #
# This module defines a class RandomForest which implements random forest      #
# based learner.                                                               #
#                                                                              #
# The implemention is based on CART algorithm which is explained in the book - #
# 'programming collective intelligence'                                        #
#                                                                              #
################################################################################



#------------------------------------------------------------------------------#
# import built-in system modules here                                          #
#------------------------------------------------------------------------------#
import sys
import random
import numpy as np
import math
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
#------------------------------------------------------------------------------#


#------------------------------------------------------------------------------#
# import package modules here                                                  #
#------------------------------------------------------------------------------#
import sources.utility.util as util
#------------------------------------------------------------------------------#



#------------------------------------------------------------------------------#
# DNode Class - represents decision tree node                                  #
#------------------------------------------------------------------------------#
class DNode:
      col = None
      value = None
      results = None
      tnode = None
      fnode = None
      leaf_node = None

      def __init__(self, col=None, value=None, results=None, tnode=None,
                   fnode=None, leaf_node=None):
          self.col = col
          self.value = value
          self.results = results
          self.tnode = tnode
          self.fnode = fnode
          self.leaf_node = leaf_node
#------------------------------------------------------------------------------#


#------------------------------------------------------------------------------#
# CART tree classifier                                                         #
#------------------------------------------------------------------------------#
class CART:
      def get_value_count(self, data_set, col):
          values = {}
          if len(data_set) == 0:
             return values
          for row in data_set:
              value = row[col]
              if value not in values:
                 values[value] = 0
              values[value] += 1
          return values

      def get_results_count(self, data_set):
          results = {}
          if len(data_set) == 0:
             return results
          last_col = len(data_set[0]) - 1
          for row in data_set:
              result = row[last_col]
              if result not in results:
                 results[result] = 0
              results[result] += 1
          return results

      def compute_entropy(self, data_set):
          results = self.get_results_count(data_set)
          n = len(data_set)
          ent = 0.0
          for v in results.values():
              p = float(v)/float(n)
              ent = ent + (p * math.log(p, 2))
          ent = -ent
          return ent

      def compute_gini_impurity(self, data_set):
          results = self.get_results_count(data_set)
          n = len(data_set)
          gi = 0.0
          for v in results.values():
              gi += np.square(float(v)/float(n))
          gi = 1.0 - gi
          return gi

      def compute_impurity(self, data_set):
          return self.compute_entropy(data_set)

      def binary_classify_based_on_value_comparison(self, data_set, col, value):
          set1 = []
          set2 = []
          for row in data_set:
              if row[col] >= value:
                 set1.append(row)
              else:
                 set2.append(row)
          return set1, set2

      def banary_classfy_based_on_value_equality(self, data_set, col, value):
          set1 = []
          set2 = []
          for row in data_set:
              if row[col] == value:
                 set1.append(row)
              else:
                 set2.append(row)
          return set1, set2

      def binary_classify_data_set(self, data_set, col, value):
          binary_classifier = None
          if isinstance(value, int) or isinstance(value, float):
             binary_classifier = self.binary_classify_based_on_value_comparison
          else:
             binary_classifier = self.banary_classfy_based_on_value_equality
          return binary_classifier(data_set, col, value)

      def select_random_subset_of_features(self, col_count):
          column_list = []
          for i in range(0, col_count):
              column_list.append(i)
          r_col_count = int(math.sqrt(col_count))
          r_col_list = random.sample(column_list, r_col_count)
          r_col_dict = {}
          for i in range(0, r_col_count):
              r_col_dict[i] = i
          return r_col_dict

      def get_best_partition(self, data_set):
          col_count = len(data_set[0]) - 1
          r_col_dict = self.select_random_subset_of_features(col_count)
          set_impurity = self.compute_impurity(data_set)
          best_gain = 0.0;
          best_combination = None
          best_partition = None
          for col in range(0, col_count):
              if col not in r_col_dict:
                 continue

              values = self.get_value_count(data_set, col)
              for k in values.keys():
                  # there are missing values, simply skip over these values
                  if k == '?':
                     continue
                  set1, set2 = self.binary_classify_data_set(data_set, col, k)
                  set1_impurity = self.compute_impurity(set1)
                  set2_impurity = self.compute_impurity(set2)
                  p = float(len(set1)) / float(len(data_set))
                  weighted_impurity = (p * set1_impurity) + \
                                                   ((1-p) * set2_impurity)
                  gain = set_impurity - weighted_impurity
                  if gain > best_gain and len(set1) > 0 and len(set2) > 0:
                     best_gain = gain
                     best_combination = (col, k)
                     best_partition = (set1, set2)
          return best_gain, best_combination, best_partition

      def recursive_build_tree(self, data_set):
          if len(data_set) == 0:
             return DNode(leaf_node=True)

          best_gain, best_combination, best_partition = \
                                               self.get_best_partition(data_set)
          if best_gain > 0.0:
             tb = self.recursive_build_tree(best_partition[0])
             fb = self.recursive_build_tree(best_partition[1])
             pnode = DNode(col=best_combination[0], value=best_combination[1], \
                           tnode=tb, fnode=fb, leaf_node=False)
             return pnode
          else:
             results_dict = self.get_results_count(data_set)
             lnode = DNode(results=results_dict, leaf_node=True)
             return lnode

      def build_tree(self, data_set):
          root = self.recursive_build_tree(data_set)
          return root
#------------------------------------------------------------------------------#


#------------------------------------------------------------------------------#
# RandomForest Class                                                           #
#------------------------------------------------------------------------------#
class RandomForest:
      # contruct the classification tree for training data
      def build_tree(self, data_set):
          cart = CART()
          return cart.build_tree(data_set)

      # preprocess the data set
      def preprocess_data_set(self, data_set):
          rows = len(data_set)
          cols = len(data_set[0])

          for r in range(0, rows):
              # missing chromosome numbers
              if data_set[r][444] == '?':
                 data_set[r][444] = '7'
              # convert chromosome numbers to int type
              data_set[r][444] = int(data_set[r][444])
              # delete 'extra full stop' at the end of the line
              data_set[r][2959] = data_set[r][2959][:-1]
              # delete first column which represents the gene type
              del data_set[r][0]
              # delete all function class as they should not be used
              # as features
              del data_set[r][2944:2958]

          return data_set

      def get_gene_list(self, data):
          gene_list = []
          for row in data:
              gene_list.append(row[0])
          return gene_list

      def get_class(self, results):
          cur_v = 0
          cur_k = None
          for k, v in results.items():
              if v > cur_v:
                 cur_v = v
                 cur_k = k
          return cur_k

      def select_branch_based_on_value_comparison(self, tree, row):
          node = None
          t_col = tree.col
          t_val = tree.value
          if row[t_col] >= t_val:
             node = tree.tnode
          else:
             node = tree.fnode
          return node

      def select_branch_based_on_value_equality(self, tree, row):
          node = None
          t_col = tree.col
          t_val = tree.value
          if row[t_col] == t_val:
             node = tree.tnode
          else:
             node = tree.fnode
          return node

      def select_branch(self, tree, row):
          cur_select_branch = None
          t_val = tree.value
          if isinstance(t_val, int) or isinstance(t_val, float):
             cur_select_branch = self.select_branch_based_on_value_comparison
          else:
             cur_select_branch = self.select_branch_based_on_value_equality
          return cur_select_branch(tree, row)

      # recursively classify the given test data item
      def recursive_classify(self, tree, row):
          if tree.leaf_node == False:
             node = self.select_branch(tree, row)
             return self.recursive_classify(node, row)
          else:
             return tree

      # classify the test data
      def classify(self, roots, test_data):
          # save gene listi before pre-processing
          gene_list = self.get_gene_list(test_data)

          # preprocess test data
          processed_test_data = self.preprocess_data_set(test_data)

          # classify test data
          class_dict = {}
          for r in range(0, len(processed_test_data)):
              row = processed_test_data[r]
              cur_gene = gene_list[r]
              # select class for from each tree for the 'row'
              tree_dict = {}
              for t in range(0, len(roots)):
                  node = self.recursive_classify(roots[t], row)
                  cc = self.get_class(node.results)
                  if cc not in tree_dict:
                     tree_dict[cc] = 0
                  tree_dict[cc] += 1

              # select the class which is most frequently selected
              # in the above classification process
              c_val = 0
              for k, v in tree_dict.items():
                  if v > c_val:
                     c_val = v
                     class_dict[cur_gene] = k

          return class_dict

      # ask classification tree learner to learn from training data
      def learn(self, training_data):
          # preprocess the data set
          processed_data_set = self.preprocess_data_set(training_data)

          # train total_trees number of trees
          total_trees = 200
          # randomly select 2/3rd of data set items for every tree to be 
          # trained
          r_len = 2 * int(len(training_data)/3)
          roots = []
          for i in range(0, total_trees):
              sampled_data_set = random.sample(processed_data_set, r_len)
              roots.append(self.build_tree(sampled_data_set))

          # return roots of learned trees
          return roots
#------------------------------------------------------------------------------#