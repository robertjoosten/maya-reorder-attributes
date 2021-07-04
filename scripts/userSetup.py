from maya import cmds


def main():
    from reorder_attributes import install
    install.execute()


if not cmds.about(batch=True):
    cmds.evalDeferred(main)
