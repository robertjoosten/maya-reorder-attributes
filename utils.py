import os
import sys
from maya import OpenMaya, cmds

class UndoContext(object):
    """
    The undo context is used to combine a chain of commands into one undo.
    Can be used in combination with the "with" statement.
    
    with UndoContext():
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
    