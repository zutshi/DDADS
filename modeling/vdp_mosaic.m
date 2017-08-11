path = '/home/zutshi/work/projects/DDADS/branches/proto/data/vdp/';

%% Train
load([path 'vdp_data_1e4_t02.mat'])
X_train = Y_summary(:, 1:2);
Y_train = Y_summary(:, 3:4);
y1_train = Y_train(:,1);
y2_train = Y_train(:,2);

bound = 1e-0;
[H1, guards1] = genPiecewiseAffineModel(X_train, y1_train, bound);
[H2, guards2] = genPiecewiseAffineModel(X_train, y2_train, bound);

y1_ = getValue(guards1, H1, X_train);
y2_ = getValue(guards2, H2, X_train);
fprintf('Training mse:\n')
sqrt(mean((y1_-y1_train).^2))
sqrt(mean((y2_-y2_train).^2))

%% Test
load([path 'vdp_data_1e3_t02.mat'])

X_test = Y_summary(:, 1:2);
Y_test = Y_summary(:, 3:4);
y1_test = Y_test(:,1);
y2_test = Y_test(:,2);

y1_ = getValue(guards1, H1, X_test);
y2_ = getValue(guards2, H2, X_test);
fprintf('Testing mse:\n')
sqrt(mean((y1_-y1_test).^2))
sqrt(mean((y2_-y2_test).^2))
