# TODO:
# dynamicall generate an opt class to mimic the same defined in
# loadsystem.py
# switch this to a reg class later.
#Options = type(str('Options'), (), {})
opts = None


debug = False
debug_plot = False
plot = False

paper_plot = False

# CE hack is ON
CE = True
BLOCK = False


# def plt_show():
#     from matplotlib import pyplot as plt
#     if debug_plot or (debug and plot):
#         plt.show(block=BLOCK)
#     else:
#         plt.close()
