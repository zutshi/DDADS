import scipy.io as spio
import sklearn.tree as sktree
from sklearn.externals.six import StringIO
from IPython import embed

mat = spio.loadmat('vdp_x_1e6_data.mat')
clf = sktree.DecisionTreeRegressor()
dtree_clf = clf.fit(mat['X'], mat['Y'][:, 0])

print (dtree_clf.max_depth)
print (dtree_clf.get_params())

dot_data = StringIO
sktree.export_graphviz(dtree_clf, out_file='dot_data', feature_names=['x1', 'x2'], filled=True, rounded=True, impurity=False)
# dtree_clf.decision_path()
