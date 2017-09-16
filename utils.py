import os
import sys
from maya import OpenMaya, cmds

class UndoStateContext(object):
    """
    The undo state is used to force undo commands to be registered when this
    tool is being used. Once the "with" statement is being exited, the default
    settings are restored.
    
    with UndoStateContext():
        # code
    """
    def __init__(self):
        self.state = cmds.undoInfo(query=True, state=True)
        self.infinity = cmds.undoInfo(query=True, infinity=True)
        self.length = cmds.undoInfo(query=True, length=True)

    def __enter__(self):
        cmds.undoInfo(state=True, infinity=True)
        
    def __exit__(self, *exc_info):
        cmds.undoInfo(
            state=self.state, 
            infinity=self.infinity, 
            length=self.length
        )

class UndoChunkContext(object):
    """
    The undo context is used to combine a chain of commands into one undo.
    Can be used in combination with the "with" statement.
    
    with UndoChunkContext():
        # code
    """
    def __enter__(self):
        cmds.undoInfo(openChunk=True)
        
    def __exit__(self, *exc_info):
        cmds.undoInfo(closeChunk=True)
        
        
def getLastSelectedNode():
    """
    Query the current selection with the Maya API and return the last item on
    the selection list. The reason the API has to be used is that there is a 
    delay with cmds, not returning the right node. This function gets called
    as a result of a OpenMaya.MModelMessage.kActiveListModified callback.
    
    :return: Full name of latest selected object.
    :rtype: str
    """
    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selection)
    
    num = selection.length()
    if not num:
        return

    dag = OpenMaya.MDagPath()
    selection.getDagPath(num-1, dag)
    return dag.fullPathName()
    