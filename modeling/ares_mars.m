% load('/home/zutshi/work/projects/S3CAMR/master/matlab_proto/vdp_data_1e3_t02.mat')
load('/home/zutshi/work/projects/S3CAMR/master/matlab_proto/vdp_data_1e4_t02.mat')
X = Y_summary(:, 1:2);
Y = Y_summary(:, 3:4);
y1 = Y(:,1);
y2 = Y(:,2);

params = aresparams2('maxFinalFuncs', 20, 'maxInteractions', 2, 'c', 0, 'cubic', 0, 'useMinSpan', -1, 'useEndSpan', -1, 'threshold', 1e-4, 'allowLinear', 1);
[model1, ~, resultsEval1] = aresbuild(X, y1, params);

aresinfo(model1, X, y1);
areseq(model1, 3);
aresplot(model1, [1 2]);
hold on;
plot3(X(:,1), X(:,2), y1, 'r.')

params = aresparams2('maxFinalFuncs', 20, 'maxInteractions', 2, 'c', 0, 'cubic', 0, 'useMinSpan', -1, 'useEndSpan', -1, 'threshold', 1e-4, 'allowLinear', 1);
[model2, ~, resultsEval2] = aresbuild(X, y2, params);

aresinfo(model2, X, y2);
areseq(model2, 3);
aresplot(model2, [1 2]);
hold on;
plot3(X(:,1), X(:,2), y2, 'r.')

% params = aresparams2('maxFinalFuncs', 10, 'maxInteractions', 2, 'c', 0, 'cubic', 0, 'useMinSpan', -1, 'useEndSpan', -1, 'threshold', 1e-4, 'allowLinear', 1);
% [model1, ~, resultsEval] = aresbuild(X, y1, params);
% 
% aresplot(model1, [1 2]);
% hold on;
% plot3(X(:,1), X(:,2), y1, '.')

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
load('/home/zutshi/work/projects/S3CAMR/master/matlab_proto/vdp_data_1e4_t02.mat')
X = Y_summary(:, 1:2);
Y = Y_summary(:, 3:4);
y1 = Y(:,1);
y2 = Y(:,2);