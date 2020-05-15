import gc


# 内存回收
def clear_all_var():
    for x in locals().keys():
        del locals()[x]
    gc.collect()
